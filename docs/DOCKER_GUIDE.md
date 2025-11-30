# Docker Deployment Guide - PAPL Converter

## Quick Start with Docker Compose

### Prerequisites
- Docker Desktop installed (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- 2GB RAM allocated to Docker
- At least 1GB disk space

### Simple Start

```bash
# Extract the app
unzip papl_converter_app_CORRECTED.zip
cd papl_converter

# Build and start with one command
docker-compose up --build

# Access the app at:
# http://localhost:8501
```

### Stop the App

```bash
# Stop the container (Ctrl+C in terminal, then:)
docker-compose down

# Or force stop:
docker-compose down --remove-orphans
```

---

## Detailed Docker Commands

### Build Only (No Start)

```bash
# Build the image
docker-compose build

# Build with no cache (fresh build)
docker-compose build --no-cache
```

### Run in Background (Detached Mode)

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop background containers
docker-compose down
```

### Development Mode

For active development with live code updates:

```bash
# Uncomment volume mounts in docker-compose.yml:
# - ./pages:/app/pages
# - ./lib:/app/lib

# Then run with:
docker-compose up
```

Now code changes will be reflected immediately without rebuilding!

---

## Docker Compose Configuration Explained

### Port Mapping
```yaml
ports:
  - "8501:8501"
```
- Maps container port 8501 to host port 8501
- Access app at http://localhost:8501
- Change if port 8501 is in use: "8080:8501" → http://localhost:8080

### Volume Mounts
```yaml
volumes:
  - ./outputs:/app/outputs
```
- Persists generated files (JSON, YAML, Markdown)
- Files saved in local `./outputs` directory
- Survives container restarts

### Environment Variables
```yaml
environment:
  - STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
```
- 200MB max file upload (increase if needed)
- Adjust for very large PAPL files

### Health Check
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
  interval: 30s
```
- Monitors app health
- Auto-restarts if unhealthy
- View status: `docker-compose ps`

### Restart Policy
```yaml
restart: unless-stopped
```
- Auto-restarts container if it crashes
- Starts on system boot
- Stops only when manually stopped

---

## Using Standalone Docker (Without Compose)

### Build Image

```bash
docker build -t papl-converter .
```

### Run Container

```bash
docker run -d \
  --name papl-converter \
  -p 8501:8501 \
  -v $(pwd)/outputs:/app/outputs \
  -e STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200 \
  papl-converter
```

### View Logs

```bash
docker logs -f papl-converter
```

### Stop Container

```bash
docker stop papl-converter
docker rm papl-converter
```

---

## Troubleshooting

### Issue: Port Already in Use

**Error:** `Bind for 0.0.0.0:8501 failed: port is already allocated`

**Solution:**
```bash
# Option 1: Stop conflicting container
docker ps  # Find container using port 8501
docker stop <container-id>

# Option 2: Use different port
# Edit docker-compose.yml:
ports:
  - "8080:8501"  # Use 8080 instead
```

### Issue: Build Fails

**Error:** Various build errors

**Solution:**
```bash
# Clean build with no cache
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Issue: Container Keeps Restarting

**Error:** Container exits immediately

**Solution:**
```bash
# Check logs for errors
docker-compose logs papl-converter

# Common fixes:
# 1. Check requirements.txt is valid
# 2. Verify Dockerfile syntax
# 3. Ensure app.py exists
```

### Issue: Cannot Upload Files

**Error:** File upload fails or times out

**Solution:**
```bash
# Increase upload size in docker-compose.yml:
environment:
  - STREAMLIT_SERVER_MAX_UPLOAD_SIZE=500  # Increase to 500MB
```

### Issue: Outputs Not Persisting

**Error:** Generated files disappear after restart

**Solution:**
```bash
# Verify volume mount in docker-compose.yml:
volumes:
  - ./outputs:/app/outputs  # Should be uncommented

# Create outputs directory if missing:
mkdir -p outputs
```

### Issue: Container Unhealthy

**Error:** Health check failing

**Solution:**
```bash
# Check container status
docker-compose ps

# If unhealthy, check logs
docker-compose logs

# Common cause: App not starting properly
# Fix: Check app.py for errors
```

---

## Production Deployment

### Using Docker Compose in Production

```bash
# Production docker-compose.yml settings:

version: '3.8'
services:
  papl-converter:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./outputs:/app/outputs
    environment:
      - STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    restart: always  # Changed from unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Behind Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/papl-converter

server {
    listen 80;
    server_name papl.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### With SSL (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d papl.yourdomain.com

# Certbot will auto-configure nginx for HTTPS
```

---

## Monitoring and Maintenance

### Check Container Status

```bash
# List running containers
docker-compose ps

# View resource usage
docker stats papl-converter
```

### View Logs

```bash
# All logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100
```

### Access Container Shell

```bash
# Open bash in running container
docker-compose exec papl-converter /bin/bash

# Once inside:
ls -la          # List files
cat app.py      # View files
python --version  # Check Python version
exit            # Leave container
```

### Backup Outputs

```bash
# Outputs are in ./outputs directory
# Backup with:
tar -czf papl-outputs-backup-$(date +%Y%m%d).tar.gz outputs/

# Restore:
tar -xzf papl-outputs-backup-YYYYMMDD.tar.gz
```

### Update Application

```bash
# Pull latest code
git pull  # If using git

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Performance Tuning

### Increase Resources

Edit docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Max 4 CPUs
      memory: 8G     # Max 8GB RAM
    reservations:
      cpus: '2'      # Min 2 CPUs
      memory: 4G     # Min 4GB RAM
```

### Optimize for Large Files

```yaml
environment:
  - STREAMLIT_SERVER_MAX_UPLOAD_SIZE=500  # 500MB uploads
  - STREAMLIT_SERVER_MAX_MESSAGE_SIZE=500  # 500MB messages
```

---

## Multi-Container Setup (Advanced)

For running multiple instances:

```yaml
version: '3.8'

services:
  papl-converter-1:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./outputs-1:/app/outputs

  papl-converter-2:
    build: .
    ports:
      - "8502:8501"
    volumes:
      - ./outputs-2:/app/outputs

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - papl-converter-1
      - papl-converter-2
```

---

## Security Best Practices

### Don't Expose Directly to Internet

```bash
# Use nginx reverse proxy
# Configure firewall
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 8501/tcp  # Block direct access
```

### Use Docker Secrets (Production)

```yaml
services:
  papl-converter:
    secrets:
      - api_key
secrets:
  api_key:
    file: ./secrets/api_key.txt
```

### Regular Updates

```bash
# Update base image
docker pull python:3.11-slim

# Rebuild
docker-compose build --no-cache
```

---

## Common Docker Commands Reference

```bash
# Build and Start
docker-compose up --build           # Build and start
docker-compose up -d                # Start in background
docker-compose up --build -d        # Build and start in background

# Stop and Remove
docker-compose down                 # Stop and remove containers
docker-compose down -v              # Also remove volumes
docker-compose down --remove-orphans # Remove unused containers

# View and Monitor
docker-compose ps                   # List containers
docker-compose logs -f              # Follow logs
docker-compose logs --tail=50       # Last 50 lines
docker stats                        # Resource usage

# Execute Commands
docker-compose exec papl-converter bash      # Access shell
docker-compose exec papl-converter ls -la    # Run command

# Cleanup
docker system prune                 # Remove unused data
docker system prune -a              # Remove all unused images
docker volume prune                 # Remove unused volumes
```

---

## Success Checklist

✅ Docker installed and running  
✅ Extracted papl_converter_app_CORRECTED.zip  
✅ Navigated to papl_converter directory  
✅ Ran `docker-compose up --build`  
✅ Accessed http://localhost:8501  
✅ Uploaded PAPL and Support Catalogue  
✅ Ran conversion successfully  
✅ Downloaded generated files from outputs/  

**You're ready to run the PAPL Converter with Docker!** 🐳
