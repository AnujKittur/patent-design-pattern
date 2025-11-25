# How to Run and Share Your Patent Design Website

This guide will walk you through running the application and sharing it with others.

## 🚀 Quick Start: Run Locally

### Step 1: Prerequisites Check

First, make sure you have Docker installed:

```bash
# Check if Docker is installed
docker --version
docker-compose --version
```

If not installed, download from:
- **Mac**: https://www.docker.com/products/docker-desktop
- **Windows**: https://www.docker.com/products/docker-desktop
- **Linux**: `sudo apt-get install docker.io docker-compose`

### Step 2: Set Up Environment

```bash
# Navigate to your project directory
cd /Users/anuj_kittur/Desktop/Scraper

# Create environment file
cp .env.example .env

# Edit .env file (optional - add your OpenAI API key for better performance)
nano .env
# OR
open .env  # On Mac
```

Add your OpenAI API key if you have one:
```
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Run the Deployment Script

```bash
# Make script executable (if not already)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Create data directories
- ✅ Build Docker images
- ✅ Start all services

### Step 4: Access Your Website

Once deployment is complete, access your website at:

- **Frontend (Main Website)**: http://localhost:8501
- **API Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Step 5: Test the Website

1. Open your browser
2. Go to http://localhost:8501
3. Enter a design prompt like: "Design a robotic bricklaying system"
4. Click "Generate Design"
5. Wait for the design brief to be generated

## 🌐 Share with Others: Different Options

### Option A: Local Network Sharing (Quick & Easy)

If you want others on your local network to access it:

1. **Find your local IP address:**

   **Mac/Linux:**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
   
   **Windows:**
   ```cmd
   ipconfig
   ```
   
   Look for something like: `192.168.1.XXX` or `10.0.0.XXX`

2. **Update streamlit_app.py to allow external access:**

   The app is already configured to accept connections. Just share:
   - **Frontend**: `http://YOUR_IP:8501`
   - **API**: `http://YOUR_IP:8000`

3. **Example:**
   - If your IP is `192.168.1.100`
   - Share: `http://192.168.1.100:8501`

4. **Important:** Make sure your firewall allows connections on ports 8501 and 8000

### Option B: Production Deployment with Domain (For Public Sharing)

Use the production setup with Nginx:

```bash
# Stop current deployment (if running)
docker-compose down

# Start production deployment
docker-compose -f docker-compose.prod.yml up --build -d
```

This will serve everything on port 80 (standard HTTP port).

**To share publicly, you need:**
1. A server (AWS EC2, DigitalOcean, etc.) with a public IP
2. A domain name (optional but recommended)
3. Port forwarding configured

### Option C: Cloud Deployment (Easiest for Sharing)

Deploy to a cloud platform for easy public access:

#### Railway.app (Recommended - Free tier available)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize project:**
   ```bash
   railway init
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

5. **Get public URL:**
   ```bash
   railway domain
   ```
   
   Railway will provide a public URL like: `https://your-app.railway.app`

#### Render.com (Free tier available)

1. **Create account** at https://render.com
2. **Connect GitHub repository** (push your code to GitHub first)
3. **Create new Web Service**
4. **Select your repository**
5. **Use these settings:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
   - **Environment**: Python 3
6. **Add environment variables:**
   - `OPENAI_API_KEY`: Your API key (if you have one)
   - `API_URL`: Will be auto-generated
7. **Deploy!**

Render will provide a public URL like: `https://your-app.onrender.com`

#### Heroku (Free tier limited)

1. **Install Heroku CLI:**
   ```bash
   # Mac
   brew install heroku/brew/heroku
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login:**
   ```bash
   heroku login
   ```

3. **Create apps:**
   ```bash
   heroku create patent-design-api
   heroku create patent-design-frontend
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set OPENAI_API_KEY=your-key -a patent-design-api
   heroku config:set OPENAI_API_KEY=your-key -a patent-design-frontend
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

## 📋 Step-by-Step: Run and Share (Local Network)

Here's the complete process:

### 1. Start the Services

```bash
cd /Users/anuj_kittur/Desktop/Scraper

# If first time, run:
./deploy.sh

# If already set up, just start:
docker-compose up -d
```

### 2. Verify Services are Running

```bash
# Check if containers are running
docker-compose ps

# Check logs
docker-compose logs -f

# Test API health
curl http://localhost:8000/health
```

### 3. Get Your IP Address

```bash
# Mac/Linux
ipconfig getifaddr en0  # Or en1, depending on your network interface

# Or use:
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### 4. Configure Firewall (if needed)

**Mac:**
```bash
# Allow incoming connections on ports 8501 and 8000
sudo pfctl -f /etc/pf.conf
```

**Linux:**
```bash
sudo ufw allow 8501/tcp
sudo ufw allow 8000/tcp
```

**Windows:**
- Go to Windows Firewall settings
- Add inbound rules for ports 8501 and 8000

### 5. Share the Link

Share with others:
- **Website**: `http://YOUR_IP:8501`
- **Example**: `http://192.168.1.100:8501`

### 6. Access Remotely

Others can now:
1. Open their browser
2. Go to the shared URL
3. Use the website just like you do locally

## 🔧 Troubleshooting

### Website Not Loading

1. **Check if services are running:**
   ```bash
   docker-compose ps
   ```

2. **Check logs:**
   ```bash
   docker-compose logs frontend
   docker-compose logs api
   ```

3. **Restart services:**
   ```bash
   docker-compose restart
   ```

### Can't Access from Other Devices

1. **Check IP address is correct:**
   ```bash
   ifconfig | grep "inet "
   ```

2. **Check firewall settings**

3. **Verify devices are on same network**

4. **Try accessing from your own device using IP instead of localhost:**
   ```
   http://YOUR_IP:8501
   ```

### Port Already in Use

```bash
# Find process using port
lsof -i :8501
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

## 🎯 Recommended Setup for Sharing

### For Quick Testing (Local Network):
- ✅ Use `docker-compose up`
- ✅ Share `http://YOUR_IP:8501`
- ✅ Works for same WiFi/network

### For Public Sharing:
- ✅ Deploy to Railway.app or Render.com
- ✅ Get public URL automatically
- ✅ No firewall configuration needed
- ✅ Accessible from anywhere

### For Production:
- ✅ Use `docker-compose.prod.yml`
- ✅ Set up domain name
- ✅ Configure SSL/HTTPS
- ✅ Use cloud server (AWS, DigitalOcean)

## 📝 Quick Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Check status
docker-compose ps

# Rebuild and restart
docker-compose up --build -d
```

## 🆘 Need Help?

1. Check logs: `docker-compose logs -f`
2. Verify health: `curl http://localhost:8000/health`
3. Check documentation: `DEPLOYMENT.md`
4. Review configuration: `.env` file

---

**Your website is now ready to share!** 🎉

