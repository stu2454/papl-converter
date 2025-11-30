# Quick Port Change Guide - Using Port 8502

## You Changed to Port 8502 ✅

Since port 8501 is already in use, here's how to use port 8502:

---

## Method 1: Using .env File (Easiest)

A `.env` file has been created for you with port 8502:

```bash
# Just run Docker Compose normally
docker-compose up --build

# Access at:
http://localhost:8502
```

The `.env` file contains:
```env
STREAMLIT_SERVER_PORT=8502
```

Docker Compose will automatically pick this up!

---

## Method 2: Edit docker-compose.yml Directly

If you want to hardcode the port, edit `docker-compose.yml`:

```yaml
services:
  papl-converter:
    ports:
      - "8502:8501"  # Changed from "8501:8501"
```

**Explanation:**
- `"8502:8501"` means: host port 8502 → container port 8501
- Access at http://localhost:8502

---

## Method 3: Override on Command Line

```bash
# Set port via environment variable
STREAMLIT_SERVER_PORT=8502 docker-compose up --build

# Or specify in docker-compose command
docker-compose up --build -e STREAMLIT_SERVER_PORT=8502
```

---

## Verification Steps

### 1. Check the Port is Free
```bash
# Check if 8502 is available
lsof -i :8502
# Should return nothing (port is free)

# Or use netstat
netstat -an | grep 8502
# Should return nothing
```

### 2. Start the App
```bash
docker-compose up --build
```

### 3. Verify It's Running
```bash
# Check container logs
docker-compose logs | grep "You can now view"
# Should show: "You can now view your Streamlit app in your browser"
# And: "Network URL: http://0.0.0.0:8502"

# Test the endpoint
curl http://localhost:8502
# Should return HTML
```

### 4. Access in Browser
```
http://localhost:8502
```

---

## If You Need to Change Again

### To Port 8503:
```bash
# Edit .env file
nano .env
# Change: STREAMLIT_SERVER_PORT=8503

# Restart
docker-compose down
docker-compose up
```

### To Port 9000:
```bash
# Edit .env file
echo "STREAMLIT_SERVER_PORT=9000" > .env

# Restart
docker-compose down
docker-compose up
```

---

## Troubleshooting

### Issue: Still Can't Access on 8502

**Check container is running:**
```bash
docker-compose ps
# Should show "healthy" status
```

**Check port mapping:**
```bash
docker ps
# Look for: 0.0.0.0:8502->8501/tcp
```

**Check logs:**
```bash
docker-compose logs -f
# Look for: "You can now view your Streamlit app"
```

### Issue: Port 8502 Also in Use

**Find what's using it:**
```bash
lsof -i :8502
# Or
netstat -tulpn | grep 8502
```

**Use a different port:**
```bash
# Edit .env
echo "STREAMLIT_SERVER_PORT=8503" > .env

# Restart
docker-compose down
docker-compose up
```

---

## Your Current Setup

✅ Port: **8502**  
✅ Access: **http://localhost:8502**  
✅ Configuration: **.env file**  
✅ Docker Compose: **Automatic**  

---

## Quick Reference Commands

```bash
# Start app
docker-compose up --build

# Access browser
open http://localhost:8502

# View logs
docker-compose logs -f

# Stop app
docker-compose down

# Restart with different port
echo "STREAMLIT_SERVER_PORT=8503" > .env
docker-compose up

# Check what ports are in use
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

---

## Files Modified

✅ `.env` created with `STREAMLIT_SERVER_PORT=8502`  
✅ `docker-compose.yml` already configured to read .env  
✅ No code changes needed  

**Just run `docker-compose up --build` and access on port 8502!** 🚀
