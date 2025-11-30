"""
LLM-Powered PAPL Assistant with RAG using AWS Bedrock
Real production implementation with Claude on Bedrock + embeddings
Uses environment variables for AWS credentials - no hardcoded secrets!
"""

import json
import yaml
import os
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import re
import numpy as np
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load from .env file if present
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("Info: python-dotenv not installed. Using system environment variables only.")

# AWS Bedrock imports
try:
    import boto3
    from botocore.config import Config
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    print("Warning: boto3 not installed. Install with: pip install boto3")


@dataclass
class Document:
    """Document chunk for RAG"""
    content: str
    metadata: Dict[str, Any]
    source_type: str  # 'pricing', 'rule', 'guidance'
    chunk_id: str
    embedding: Optional[np.ndarray] = None


class BedrockRAGAssistant:
    """Production RAG assistant using AWS Bedrock"""
    
    def __init__(self, 
                 json_data=None, 
                 yaml_data=None, 
                 markdown_data=None,
                 aws_region=None,
                 embedding_model=None,
                 llm_model=None):
        """
        Initialize Bedrock RAG Assistant
        
        AWS credentials are loaded from environment variables:
        - AWS_ACCESS_KEY_ID (optional - uses default credential chain if not set)
        - AWS_SECRET_ACCESS_KEY (optional)
        - AWS_SESSION_TOKEN (optional - for temporary credentials)
        - AWS_REGION (optional - defaults to ap-southeast-2)
        - BEDROCK_EMBEDDING_MODEL (optional)
        - BEDROCK_LLM_MODEL (optional)
        
        Args:
            json_data: PAPL pricing data (JSON)
            yaml_data: PAPL claiming rules (YAML)
            markdown_data: PAPL guidance (Markdown)
            aws_region: AWS region (default from env or ap-southeast-2)
            embedding_model: Bedrock embedding model (default from env or Titan)
            llm_model: Bedrock LLM model (default from env or Claude Sonnet)
        """
        self.json_data = json_data or {}
        self.yaml_data = yaml_data or {}
        self.markdown_data = markdown_data or ""
        
        # AWS Bedrock configuration from environment variables
        self.aws_region = (
            aws_region or 
            os.getenv('AWS_REGION') or 
            os.getenv('AWS_DEFAULT_REGION') or 
            'ap-southeast-2'  # Sydney default for Australian data sovereignty
        )
        
        self.embedding_model = (
            embedding_model or 
            os.getenv('BEDROCK_EMBEDDING_MODEL') or 
            'amazon.titan-embed-text-v1'
        )
        
        self.llm_model = (
            llm_model or 
            os.getenv('BEDROCK_LLM_MODEL') or 
            'anthropic.claude-3-sonnet-20240229-v1:0'
        )
        
        # Initialize Bedrock clients
        if BEDROCK_AVAILABLE:
            self._init_bedrock_clients()
        else:
            raise ImportError("boto3 required for Bedrock. Install with: pip install boto3")
        
        # Document corpus
        self.documents = []
        self.conversation_history = []
        
        # Build and embed documents
        self._build_document_corpus()
        self._embed_all_documents()
    
    def _init_bedrock_clients(self):
        """
        Initialize AWS Bedrock clients using standard credential chain
        
        Credential search order:
        1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        2. Shared credential file (~/.aws/credentials)
        3. AWS config file (~/.aws/config)
        4. IAM role (for EC2/ECS/Lambda)
        
        NO HARDCODED CREDENTIALS - uses boto3's credential chain
        """
        config = Config(
            region_name=self.aws_region,
            read_timeout=300,
            retries={'max_attempts': 3}
        )
        
        # Bedrock Runtime client for inference
        # boto3 automatically finds credentials from environment or AWS config
        self.bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            config=config
            # No credentials passed - uses default credential chain
        )
        
        # Regular Bedrock client for model info (optional)
        self.bedrock = boto3.client(
            service_name='bedrock',
            config=config
        )
        
        print(f"✓ AWS Bedrock initialized in region: {self.aws_region}")
        print(f"✓ Embedding model: {self.embedding_model}")
        print(f"✓ LLM model: {self.llm_model}")
        print(f"✓ Credentials: Using boto3 credential chain (env vars, AWS config, or IAM role)")
    
    def _build_document_corpus(self):
        """Build chunked document corpus for RAG retrieval"""
        print("Building document corpus...")
        
        # Chunk 1: Each support item as a document
        if 'support_items' in self.json_data:
            for item in self.json_data['support_items']:
                doc = self._create_pricing_document(item)
                self.documents.append(doc)
        
        # Chunk 2: Each claiming rule as a document
        if 'claiming_rules' in self.yaml_data:
            for rule_name, rule_content in self.yaml_data['claiming_rules'].items():
                doc = self._create_rule_document(rule_name, rule_content)
                self.documents.append(doc)
        
        # Chunk 3: Guidance sections (split by headers)
        guidance_docs = self._create_guidance_documents(self.markdown_data)
        self.documents.extend(guidance_docs)
        
        print(f"✓ Built {len(self.documents)} document chunks")
    
    def _create_pricing_document(self, item: Dict) -> Document:
        """Convert support item to document chunk"""
        content_parts = []
        
        content_parts.append(f"Support Item: {item.get('support_item_name', 'Unknown')}")
        content_parts.append(f"Support Number: {item.get('support_item_number', 'N/A')}")
        content_parts.append(f"Category: {item.get('support_category', 'Not specified')}")
        content_parts.append(f"Registration Group: {item.get('registration_group', 'Not specified')}")
        content_parts.append(f"Unit of Measure: {item.get('unit', 'Not specified')}")
        
        # Add pricing information
        if 'price_limits' in item:
            content_parts.append("\nPricing by State:")
            for state, price_data in item['price_limits'].items():
                price = price_data.get('price', 0)
                content_parts.append(f"- {state}: ${price:.2f} per {item.get('unit', 'unit')}")
        
        # Add quote requirement
        if item.get('quote_required'):
            content_parts.append("\nNote: Quote required before claiming this support.")
        else:
            content_parts.append("\nNote: Price is set, no quote required.")
        
        content = '\n'.join(content_parts)
        
        return Document(
            content=content,
            metadata={
                'item_number': item.get('support_item_number'),
                'category': item.get('support_category'),
                'item': item
            },
            source_type='pricing',
            chunk_id=f"pricing_{item.get('support_item_number')}"
        )
    
    def _create_rule_document(self, rule_name: str, rule_content: Any) -> Document:
        """Convert claiming rule to document chunk"""
        content_parts = []
        content_parts.append(f"Claiming Rule: {rule_name.replace('_', ' ').title()}")
        content_parts.append("\nRule Details:")
        content_parts.append(yaml.dump(rule_content, default_flow_style=False))
        
        content = '\n'.join(content_parts)
        
        return Document(
            content=content,
            metadata={'rule_name': rule_name, 'rule': rule_content},
            source_type='rule',
            chunk_id=f"rule_{rule_name}"
        )
    
    def _create_guidance_documents(self, markdown: str) -> List[Document]:
        """Split markdown guidance into document chunks"""
        documents = []
        
        # Split by major headers (## level)
        sections = re.split(r'\n##\s+', markdown)
        
        for i, section in enumerate(sections):
            if section.strip():
                # Extract title (first line)
                lines = section.split('\n')
                title = lines[0] if lines else f"Section {i}"
                
                doc = Document(
                    content=section,
                    metadata={
                        'section_index': i,
                        'title': title
                    },
                    source_type='guidance',
                    chunk_id=f"guidance_{i}"
                )
                documents.append(doc)
        
        return documents
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding vector from AWS Bedrock Titan Embeddings
        
        Args:
            text: Text to embed
            
        Returns:
            numpy array of embedding vector (1536 dimensions for Titan)
        """
        # Prepare request
        body = json.dumps({
            "inputText": text
        })
        
        # Call Bedrock
        response = self.bedrock_runtime.invoke_model(
            modelId=self.embedding_model,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        embedding = response_body.get('embedding')
        
        return np.array(embedding)
    
    def _embed_all_documents(self):
        """Create embeddings for all documents using Bedrock"""
        print(f"Creating embeddings for {len(self.documents)} documents...")
        
        for i, doc in enumerate(self.documents):
            if i % 10 == 0:
                print(f"  Embedding document {i+1}/{len(self.documents)}...")
            
            # Get embedding from Bedrock
            doc.embedding = self._get_embedding(doc.content)
        
        print("✓ All documents embedded")
    
    def retrieve_relevant_documents(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Retrieve most relevant document chunks using semantic search
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            
        Returns:
            List of most relevant documents
        """
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Calculate cosine similarity with all documents
        similarities = []
        for doc in self.documents:
            if doc.embedding is not None:
                # Cosine similarity
                similarity = np.dot(query_embedding, doc.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc.embedding)
                )
                similarities.append((doc, similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, sim in similarities[:top_k]]
    
    def _generate_prompt(self, query: str, relevant_docs: List[Document]) -> str:
        """Generate prompt for Claude with retrieved context"""
        prompt_parts = []
        
        # System instructions
        prompt_parts.append("You are a helpful NDIS PAPL (Pricing Arrangements and Price Limits) assistant.")
        prompt_parts.append("Your role is to answer questions about NDIS support pricing, claiming rules, and guidance.")
        prompt_parts.append("")
        prompt_parts.append("CRITICAL RULES:")
        prompt_parts.append("1. Answer ONLY based on the provided PAPL context below")
        prompt_parts.append("2. If the answer is not in the context, say so clearly")
        prompt_parts.append("3. Always cite which document(s) you used (e.g., 'According to Document 1...')")
        prompt_parts.append("4. Use plain language suitable for participants and families")
        prompt_parts.append("5. Include support item numbers when discussing pricing")
        prompt_parts.append("6. Explain claiming rules step-by-step")
        prompt_parts.append("7. Be accurate - this affects real people's NDIS funding")
        prompt_parts.append("")
        
        # Add retrieved context
        prompt_parts.append("CONTEXT FROM PAPL DOCUMENTS:")
        prompt_parts.append("=" * 80)
        
        for i, doc in enumerate(relevant_docs, 1):
            prompt_parts.append(f"\n[Document {i} - {doc.source_type.upper()}]")
            prompt_parts.append(doc.content)
            prompt_parts.append("-" * 80)
        
        prompt_parts.append("")
        prompt_parts.append("=" * 80)
        prompt_parts.append("")
        
        # Add user query
        prompt_parts.append(f"USER QUESTION: {query}")
        prompt_parts.append("")
        
        # Instructions for response
        prompt_parts.append("Please provide a clear, accurate answer based ONLY on the context above.")
        prompt_parts.append("Remember to cite your sources and use plain language.")
        
        return '\n'.join(prompt_parts)
    
    def _call_claude_bedrock(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        Call Claude on AWS Bedrock
        
        Args:
            prompt: Full prompt with context
            max_tokens: Maximum response length
            
        Returns:
            Claude's response text
        """
        # Prepare request body for Claude 3
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # Low temperature for factual accuracy
            "top_p": 0.9
        })
        
        # Call Bedrock
        response = self.bedrock_runtime.invoke_model(
            modelId=self.llm_model,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        # Extract text from Claude's response
        answer = response_body['content'][0]['text']
        
        return answer
    
    def ask(self, query: str, top_k: int = 5, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Ask a question and get an AI-generated answer using RAG
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve
            max_tokens: Max response length
        
        Returns:
            Dict with answer, sources, and metadata
        """
        print(f"\nProcessing query: {query}")
        
        # Step 1: Retrieve relevant documents
        print(f"  → Retrieving top {top_k} relevant documents...")
        relevant_docs = self.retrieve_relevant_documents(query, top_k=top_k)
        
        if not relevant_docs:
            return {
                'answer': "I couldn't find relevant information in the PAPL documents to answer your question.",
                'sources': [],
                'retrieved_docs': 0,
                'query': query
            }
        
        print(f"  → Retrieved {len(relevant_docs)} documents")
        
        # Step 2: Generate prompt with context
        print("  → Generating prompt with context...")
        prompt = self._generate_prompt(query, relevant_docs)
        
        # Step 3: Call Claude on Bedrock
        print("  → Calling Claude on AWS Bedrock...")
        answer = self._call_claude_bedrock(prompt, max_tokens=max_tokens)
        
        print("  ✓ Response received")
        
        # Step 4: Add to conversation history
        self.conversation_history.append({
            'query': query,
            'answer': answer,
            'sources': [doc.chunk_id for doc in relevant_docs]
        })
        
        return {
            'answer': answer,
            'sources': relevant_docs,
            'retrieved_docs': len(relevant_docs),
            'query': query,
            'prompt': prompt,  # Include for debugging
            'model_used': self.llm_model
        }
    
    def chat(self, query: str) -> str:
        """
        Simple chat interface - returns just the answer text
        
        Args:
            query: User question
            
        Returns:
            AI response text
        """
        result = self.ask(query)
        return result['answer']
    
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


# Convenience alias
PAPLAssistant = BedrockRAGAssistant


# Example usage
"""
Usage Example:

from papl_assistant import BedrockRAGAssistant

# Initialize with your PAPL data
assistant = BedrockRAGAssistant(
    json_data=your_json_data,
    yaml_data=your_yaml_data,
    markdown_data=your_markdown_data,
    aws_region='ap-southeast-2',  # Sydney
    llm_model='anthropic.claude-3-sonnet-20240229-v1:0'
)

# Ask questions
result = assistant.ask("What's the price for occupational therapy in NSW?")
print(result['answer'])

# Or use simple chat interface
answer = assistant.chat("How do I claim transport support?")
print(answer)

# View sources
for doc in result['sources']:
    print(f"Source: {doc.source_type} - {doc.chunk_id}")
"""



@dataclass
class Document:
    """Document chunk for RAG"""
    content: str
    metadata: Dict[str, Any]
    source_type: str  # 'pricing', 'rule', 'guidance'
    chunk_id: str


class PAPLAssistant:
    """RAG-powered conversational assistant for PAPL queries"""
    
    def __init__(self, json_data=None, yaml_data=None, markdown_data=None):
        self.json_data = json_data or {}
        self.yaml_data = yaml_data or {}
        self.markdown_data = markdown_data or ""
        
        # Document chunks for RAG
        self.documents = []
        self.conversation_history = []
        
        # Build document corpus
        self._build_document_corpus()
    
    def _build_document_corpus(self):
        """Build chunked document corpus for RAG retrieval"""
        
        # Chunk 1: Each support item as a document
        if 'support_items' in self.json_data:
            for item in self.json_data['support_items']:
                doc = self._create_pricing_document(item)
                self.documents.append(doc)
        
        # Chunk 2: Each claiming rule as a document
        if 'claiming_rules' in self.yaml_data:
            for rule_name, rule_content in self.yaml_data['claiming_rules'].items():
                doc = self._create_rule_document(rule_name, rule_content)
                self.documents.append(doc)
