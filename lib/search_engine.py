"""
Intelligent PAPL Search Engine
Multi-format search across JSON, YAML, and Markdown with query understanding
"""

import json
import yaml
import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Structured search result"""
    source_type: str  # 'pricing', 'rule', 'guidance'
    relevance_score: float
    title: str
    content: str
    metadata: Dict[str, Any]
    match_reason: str


class PAPLSearchEngine:
    """Intelligent search across PAPL data formats"""
    
    def __init__(self, json_data=None, yaml_data=None, markdown_data=None):
        self.json_data = json_data or {}
        self.yaml_data = yaml_data or {}
        self.markdown_data = markdown_data or ""
        
        # Build search indices
        self._build_indices()
    
    def _build_indices(self):
        """Build inverted indices for fast searching"""
        self.pricing_index = {}
        self.rule_index = {}
        self.guidance_index = {}
        
        # Index support items
        if 'support_items' in self.json_data:
            for item in self.json_data['support_items']:
                self._index_support_item(item)
        
        # Index claiming rules
        if 'claiming_rules' in self.yaml_data:
            self._index_claiming_rules(self.yaml_data['claiming_rules'])
        
        # Index guidance sections
        self._index_markdown_sections(self.markdown_data)
    
    def _index_support_item(self, item: Dict):
        """Add support item to pricing index"""
        item_number = item.get('support_item_number', '')
        
        # Extract searchable terms
        terms = self._extract_terms(
            item.get('support_item_name', '') + ' ' +
            item.get('support_category', '') + ' ' +
            item.get('registration_group', '')
        )
        
        for term in terms:
            if term not in self.pricing_index:
                self.pricing_index[term] = []
            self.pricing_index[term].append(item_number)
    
    def _index_claiming_rules(self, rules: Dict):
        """Add claiming rules to rule index"""
        for rule_name, rule_content in rules.items():
            terms = self._extract_terms(rule_name)
            
            for term in terms:
                if term not in self.rule_index:
                    self.rule_index[term] = []
                self.rule_index[term].append(rule_name)
    
    def _index_markdown_sections(self, markdown: str):
        """Add markdown sections to guidance index"""
        # Split by headers
        sections = re.split(r'\n#{1,6}\s+', markdown)
        
        for i, section in enumerate(sections):
            if section.strip():
                terms = self._extract_terms(section[:200])  # First 200 chars
                
                for term in terms:
                    if term not in self.guidance_index:
                        self.guidance_index[term] = []
                    self.guidance_index[term].append(i)
    
    def _extract_terms(self, text: str) -> List[str]:
        """Extract searchable terms from text"""
        # Lowercase and split
        text = text.lower()
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-/]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        
        return words
    
    def search(self, query: str, max_results: int = 20) -> List[SearchResult]:
        """
        Intelligent search across all PAPL formats
        
        Query understanding:
        - "price for X" → Search pricing (JSON)
        - "how to claim X" → Search rules (YAML) + guidance (Markdown)
        - "can I claim X" → Search rules + pricing
        - "what is X" → Search guidance first, then pricing
        """
        results = []
        
        # Understand query intent
        intent = self._understand_query_intent(query)
        
        # Search appropriate sources based on intent
        if intent['type'] == 'pricing':
            results.extend(self._search_pricing(query, intent))
        
        if intent['type'] in ['rules', 'claiming', 'both']:
            results.extend(self._search_rules(query, intent))
        
        if intent['type'] in ['guidance', 'definition', 'both']:
            results.extend(self._search_guidance(query, intent))
        
        if intent['type'] == 'general':
            # Search everything
            results.extend(self._search_pricing(query, intent))
            results.extend(self._search_rules(query, intent))
            results.extend(self._search_guidance(query, intent))
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:max_results]
    
    def _understand_query_intent(self, query: str) -> Dict[str, Any]:
        """Understand what the user is looking for"""
        query_lower = query.lower()
        
        intent = {
            'type': 'general',
            'focus': None,
            'modifiers': []
        }
        
        # Pricing queries
        if any(word in query_lower for word in ['price', 'cost', 'how much', '$']):
            intent['type'] = 'pricing'
            intent['focus'] = 'price'
        
        # Rule/claiming queries
        elif any(phrase in query_lower for phrase in ['can i claim', 'how to claim', 'claiming', 'rules for']):
            intent['type'] = 'claiming'
            intent['focus'] = 'rules'
        
        # Definition queries
        elif any(word in query_lower for word in ['what is', 'what are', 'define', 'explain']):
            intent['type'] = 'definition'
            intent['focus'] = 'guidance'
        
        # Availability queries
        elif any(word in query_lower for word in ['can i', 'am i eligible', 'available']):
            intent['type'] = 'both'
            intent['focus'] = 'eligibility'
        
        # Extract modifiers
        if 'in nsw' in query_lower or 'in new south wales' in query_lower:
            intent['modifiers'].append(('state', 'NSW'))
        elif 'in vic' in query_lower or 'in victoria' in query_lower:
            intent['modifiers'].append(('state', 'VIC'))
        # ... other states
        
        if 'old framework' in query_lower:
            intent['modifiers'].append(('framework', 'old'))
        elif 'new framework' in query_lower:
            intent['modifiers'].append(('framework', 'new'))
        
        return intent
    
    def _search_pricing(self, query: str, intent: Dict) -> List[SearchResult]:
        """Search pricing data (JSON)"""
        results = []
        query_terms = self._extract_terms(query)
        
        # Find matching support items
        matching_items = set()
        for term in query_terms:
            if term in self.pricing_index:
                matching_items.update(self.pricing_index[term])
        
        # Get full items and score them
        for item_number in matching_items:
            item = self._get_support_item(item_number)
            if item:
                score = self._score_support_item(item, query_terms, intent)
                
                results.append(SearchResult(
                    source_type='pricing',
                    relevance_score=score,
                    title=item.get('support_item_name', 'Unknown'),
                    content=self._format_pricing_result(item, intent),
                    metadata={
                        'item_number': item_number,
                        'category': item.get('support_category', ''),
                        'item': item
                    },
                    match_reason=f"Matches: {', '.join(query_terms[:3])}"
                ))
        
        return results
    
    def _search_rules(self, query: str, intent: Dict) -> List[SearchResult]:
        """Search claiming rules (YAML)"""
        results = []
        query_terms = self._extract_terms(query)
        
        # Find matching rules
        matching_rules = set()
        for term in query_terms:
            if term in self.rule_index:
                matching_rules.update(self.rule_index[term])
        
        # Get full rules and score them
        if 'claiming_rules' in self.yaml_data:
            for rule_name in matching_rules:
                rule = self.yaml_data['claiming_rules'].get(rule_name)
                if rule:
                    score = self._score_rule(rule, query_terms, intent)
                    
                    results.append(SearchResult(
                        source_type='rule',
                        relevance_score=score,
                        title=rule_name.replace('_', ' ').title(),
                        content=self._format_rule_result(rule, intent),
                        metadata={
                            'rule_name': rule_name,
                            'rule': rule
                        },
                        match_reason=f"Claiming rule for: {rule_name}"
                    ))
        
        return results
    
    def _search_guidance(self, query: str, intent: Dict) -> List[SearchResult]:
        """Search guidance documents (Markdown)"""
        results = []
        query_terms = self._extract_terms(query)
        
        # Find matching sections
        matching_sections = set()
        for term in query_terms:
            if term in self.guidance_index:
                matching_sections.update(self.guidance_index[term])
        
        # Get full sections and score them
        sections = re.split(r'\n#{1,6}\s+', self.markdown_data)
        
        for section_idx in matching_sections:
            if section_idx < len(sections):
                section = sections[section_idx]
                score = self._score_guidance(section, query_terms, intent)
                
                # Extract section title (first line)
                lines = section.split('\n')
                title = lines[0][:100] if lines else "Guidance Section"
                
                results.append(SearchResult(
                    source_type='guidance',
                    relevance_score=score,
                    title=title,
                    content=section[:500],  # First 500 chars
                    metadata={
                        'section_index': section_idx,
                        'full_content': section
                    },
                    match_reason=f"Guidance contains: {', '.join(query_terms[:3])}"
                ))
        
        return results
    
    def _get_support_item(self, item_number: str) -> Dict:
        """Get full support item by number"""
        if 'support_items' in self.json_data:
            for item in self.json_data['support_items']:
                if item.get('support_item_number') == item_number:
                    return item
        return None
    
    def _score_support_item(self, item: Dict, query_terms: List[str], intent: Dict) -> float:
        """Score how well a support item matches the query"""
        score = 0.0
        
        # Check item name (highest weight)
        name = item.get('support_item_name', '').lower()
        name_terms = self._extract_terms(name)
        matching_terms = set(query_terms) & set(name_terms)
        score += len(matching_terms) * 3.0
        
        # Check category (medium weight)
        category = item.get('support_category', '').lower()
        if any(term in category for term in query_terms):
            score += 2.0
        
        # Check if price exists for requested state
        if intent.get('modifiers'):
            for mod_type, mod_value in intent['modifiers']:
                if mod_type == 'state':
                    if mod_value in item.get('price_limits', {}):
                        score += 1.0
        
        return score
    
    def _score_rule(self, rule: Any, query_terms: List[str], intent: Dict) -> float:
        """Score how well a rule matches the query"""
        score = 0.0
        
        # Convert rule to string for searching
        rule_str = str(rule).lower()
        
        for term in query_terms:
            if term in rule_str:
                score += 1.5
        
        # Boost if it's a claiming query
        if intent.get('focus') == 'rules':
            score *= 1.5
        
        return score
    
    def _score_guidance(self, section: str, query_terms: List[str], intent: Dict) -> float:
        """Score how well a guidance section matches"""
        score = 0.0
        
        section_lower = section.lower()
        
        for term in query_terms:
            if term in section_lower:
                score += 1.0
        
        # Boost if it's a definition query
        if intent.get('focus') == 'guidance':
            score *= 1.5
        
        return score
    
    def _format_pricing_result(self, item: Dict, intent: Dict) -> str:
        """Format pricing result for display"""
        result = f"**{item.get('support_item_name', 'Unknown')}**\n\n"
        
        # Show relevant state price if specified
        if intent.get('modifiers'):
            for mod_type, mod_value in intent['modifiers']:
                if mod_type == 'state':
                    price_data = item.get('price_limits', {}).get(mod_value, {})
                    price = price_data.get('price', 0)
                    result += f"Price in {mod_value}: ${price:.2f}\n"
        
        result += f"\nCategory: {item.get('support_category', 'Not specified')}\n"
        result += f"Unit: {item.get('unit', 'Not specified')}\n"
        
        return result
    
    def _format_rule_result(self, rule: Any, intent: Dict) -> str:
        """Format rule result for display"""
        return f"```yaml\n{yaml.dump(rule, default_flow_style=False)}\n```"
    
    def suggest_refinements(self, query: str, results: List[SearchResult]) -> List[str]:
        """Suggest query refinements based on results"""
        suggestions = []
        
        # If too many results, suggest narrowing
        if len(results) > 50:
            suggestions.append("Try being more specific (e.g., add category or state)")
        
        # If no results, suggest alternatives
        if len(results) == 0:
            query_terms = self._extract_terms(query)
            # Find similar terms in index
            similar = self._find_similar_terms(query_terms)
            if similar:
                suggestions.append(f"Did you mean: {', '.join(similar[:3])}?")
        
        # Suggest adding state if not specified
        if not any(state in query.lower() for state in ['nsw', 'vic', 'qld', 'sa', 'wa', 'tas', 'nt', 'act']):
            suggestions.append("Add your state to see local pricing (e.g., 'in NSW')")
        
        return suggestions
    
    def _find_similar_terms(self, terms: List[str]) -> List[str]:
        """Find similar terms in indices"""
        similar = []
        
        for term in terms:
            # Simple substring matching
            for indexed_term in self.pricing_index.keys():
                if term[:3] in indexed_term or indexed_term[:3] in term:
                    if indexed_term not in similar:
                        similar.append(indexed_term)
        
        return similar[:5]
