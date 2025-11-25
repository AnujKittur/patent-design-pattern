# Troubleshooting Guide: Website Not Working

## Issue 1: Docker Not Running ⚠️

**Problem:** "Cannot connect to the Docker daemon"

**Solution:**

### On Mac:
1. Open **Docker Desktop** application
2. Wait for Docker to start (whale icon in menu bar should be steady)
3. Once Docker is running, try again:
   ```bash
   docker-compose up --build
   ```

### Check if Docker is running:
```bash
docker --version
docker ps
```

If you see errors, Docker Desktop is not running. Start it first.

---

## Issue 2: Run Without Docker (Alternative)

If you can't use Docker, run directly with Python:

### Step 1: Install Dependencies
```bash
cd /Users/anuj_kittur/Desktop/Scraper
pip install -r requirements.txt
```

### Step 2: Start API Server (Terminal 1)
```bash
python app.py
```
Or:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Step 3: Start Frontend (Terminal 2)
```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### Step 4: Access Website
- Frontend: http://localhost:8501
- API: http://localhost:8000

---

## Issue 3: Ports Already in Use

**Problem:** Port 8000 or 8501 already in use

**Solution:**

### Find what's using the port:
```bash
# Mac/Linux
lsof -i :8000
lsof -i :8501

# Windows
netstat -ano | findstr :8000
```

### Kill the process:
```bash
# Mac/Linux
kill -9 <PID>

# Or use different ports in docker-compose.yml
```

### Or change ports in docker-compose.yml:
Edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
  - "8502:8501"  # Use 8502 instead of 8501
```

---

## Issue 4: Missing Environment Variables

**Problem:** Services start but can't connect to API

**Solution:**

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Edit `.env` and ensure:
```
API_URL=http://localhost:8000
OPENAI_API_KEY=your-key-here  # Optional
```

3. Restart services:
```bash
docker-compose down
docker-compose up --build
```

---

## Issue 5: Missing Data/Index

**Problem:** "Collection not found" or "No patent index"

**Solution:**

Run patent ingestion first:
```bash
# With Docker
docker-compose run --rm api python ingest.py

# Without Docker
python ingest.py
```

This will download and index patents (takes 10-30 minutes).

---

## Issue 6: Services Keep Crashing

**Check logs:**
```bash
docker-compose logs api
docker-compose logs frontend
```

**Common causes:**
1. Out of memory - Increase Docker memory allocation
2. Missing dependencies - Check requirements.txt installed
3. Port conflicts - Change ports in docker-compose.yml
4. Data directory permissions - Check `data/` folder permissions

**Fix permissions:**
```bash
chmod -R 755 data/
chown -R $USER:$USER data/
```

---

## Quick Fix Checklist

1. ✅ **Start Docker Desktop** (if using Docker)
2. ✅ **Check Docker is running**: `docker ps`
3. ✅ **Create .env file**: `cp .env.example .env`
4. ✅ **Run ingestion**: `python ingest.py` (if first time)
5. ✅ **Start services**: `docker-compose up --build`
6. ✅ **Check ports are free**: `lsof -i :8000 -i :8501`
7. ✅ **Check logs**: `docker-compose logs -f`

---

## Alternative: Run Locally (No Docker)

If Docker continues to cause issues, run directly:

### Terminal 1 - Start API:
```bash
cd /Users/anuj_kittur/Desktop/Scraper
python app.py
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2 - Start Frontend:
```bash
cd /Users/anuj_kittur/Desktop/Scraper
streamlit run streamlit_app.py
```
Wait for: `You can now view your Streamlit app in your browser.`

### Access:
- Frontend: http://localhost:8501
- API: http://localhost:8000

---

## Still Not Working?

1. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.11+
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Check firewall settings** (if sharing with others)

4. **Try different ports:**
   - Edit `app.py` and `streamlit_app.py` to use different ports
   - Or use environment variables

5. **View detailed error messages:**
   ```bash
   # Docker
   docker-compose logs --tail=100
   
   # Direct Python
   python app.py 2>&1 | tee app.log
   ```

