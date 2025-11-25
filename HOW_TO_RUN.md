# How to Run the Patent Design Website - Step by Step

## 🚀 Simplest Method (Recommended)

### Step 1: Open Terminal

Open Terminal on your Mac (Applications → Utilities → Terminal)

### Step 2: Navigate to Project

```bash
cd /Users/anuj_kittur/Desktop/Scraper
```

### Step 3: Choose Your Method

You have 2 options:

---

## Option A: Run WITHOUT Docker (Easiest - Recommended)

### Run this command:

```bash
./run_local.sh
```

This will:
- ✅ Install dependencies automatically
- ✅ Start API server in background
- ✅ Start website frontend
- ✅ Show you the access URL

**Then access:** http://localhost:8501

**To stop:** Press `Ctrl+C` in the terminal

---

## Option B: Run WITH Docker

### First: Start Docker Desktop

1. Open **Docker Desktop** from Applications
2. Wait for it to fully start (whale icon in menu bar)
3. Then run:

```bash
./fix_website.sh
```

Or manually:

```bash
docker-compose up --build
```

**Then access:** http://localhost:8501

---

## Manual Method (If Scripts Don't Work)

If you prefer to run manually, follow these steps:

### Terminal 1 - Start API Server:

```bash
cd /Users/anuj_kittur/Desktop/Scraper

# Install dependencies (first time only)
pip3 install -r requirements.txt

# Start API server
python3 app.py
```

Wait for message: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2 - Start Frontend:

Open a NEW terminal window:

```bash
cd /Users/anuj_kittur/Desktop/Scraper

# Start frontend
streamlit run streamlit_app.py
```

Wait for message with URL like: `Network URL: http://192.168.x.x:8501`

### Access Website:

Open your browser and go to: **http://localhost:8501**

---

## 📋 Quick Reference

### Check if website is running:

```bash
# Check API
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

### Stop services:

**If using Docker:**
```bash
docker-compose down
```

**If running locally:**
- Press `Ctrl+C` in both terminal windows

---

## 🔍 Troubleshooting

### "Command not found" error:
```bash
# Make scripts executable
chmod +x *.sh

# Then try again
./run_local.sh
```

### "Port already in use" error:
```bash
# Find what's using the port
lsof -i :8501

# Kill the process or use different port
```

### "Module not found" error:
```bash
# Install dependencies
pip3 install -r requirements.txt
```

### Website shows error:
1. Check both services are running (API + Frontend)
2. Make sure API is at http://localhost:8000
3. Check browser console for errors (F12)

---

## ✅ Success Checklist

After running, you should see:

- ✅ API server running on port 8000
- ✅ Frontend running on port 8501
- ✅ Can access http://localhost:8501 in browser
- ✅ Website loads and shows "Construction Robotics Design Generator"
- ✅ Can enter a prompt and generate designs

---

## 🎯 Recommended Quick Start

**For fastest setup, just run:**

```bash
cd /Users/anuj_kittur/Desktop/Scraper
./run_local.sh
```

This is the easiest method and doesn't require Docker!

