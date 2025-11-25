# Deployment Guide for Patent Design Pattern System

This guide covers deploying the Patent Design Pattern RAG system to various hosting platforms.

## Table of Contents
1. [Local Deployment with Docker](#local-deployment-with-docker)
2. [Production Deployment](#production-deployment)
3. [Cloud Platform Deployments](#cloud-platform-deployments)
4. [Environment Variables](#environment-variables)
5. [Troubleshooting](#troubleshooting)

## Local Deployment with Docker

### Prerequisites
- Docker and Docker Compose installed
- Git clone of the repository

### Steps

1. **Clone and navigate to the project:**
   ```bash
   cd /path/to/Scraper
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY (optional)
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Streamlit UI: http://localhost:8501
   - FastAPI API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Run in background:**
   ```bash
   docker-compose up -d
   ```

6. **View logs:**
   ```bash
   docker-compose logs -f
   ```

## Production Deployment

### Using Docker Compose with Nginx

1. **Use production compose file:**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

2. **Set up SSL (optional but recommended):**
   ```bash
   mkdir ssl
   # Place your SSL certificates in ./ssl/
   # Update nginx.conf for SSL configuration
   ```

3. **Access via Nginx:**
   - Frontend: http://your-domain.com/
   - API: http://your-domain.com/api/

### Manual Server Setup

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip docker.io docker-compose nginx
   ```

2. **Clone repository:**
   ```bash
   git clone <your-repo-url> /var/www/patent-design
   cd /var/www/patent-design
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

4. **Ensure data directory exists:**
   ```bash
   mkdir -p data/{raw,chunks,index,media}
   ```

5. **Run ingestion (if not done):**
   ```bash
   docker-compose run api python ingest.py
   ```

6. **Start services:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

7. **Set up systemd service (optional):**
   ```bash
   sudo nano /etc/systemd/system/patent-design.service
   ```
   ```ini
   [Unit]
   Description=Patent Design Pattern System
   Requires=docker.service
   After=docker.service

   [Service]
   Type=oneshot
   RemainAfterExit=yes
   WorkingDirectory=/var/www/patent-design
   ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
   ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
   TimeoutStartSec=0

   [Install]
   WantedBy=multi-user.target
   ```
   ```bash
   sudo systemctl enable patent-design
   sudo systemctl start patent-design
   ```

## Cloud Platform Deployments

### Railway.app

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Initialize Railway project:**
   ```bash
   railway init
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

4. **Set environment variables in Railway dashboard:**
   - `OPENAI_API_KEY`
   - `API_URL` (will be auto-generated)

### Render.com

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: patent-design-api
       env: docker
       dockerfilePath: ./Dockerfile
       dockerContext: .
       dockerCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: OPENAI_API_KEY
           sync: false
       ports:
         - port: 8000
           protocol: HTTP
     
     - type: web
       name: patent-design-frontend
       env: docker
       dockerfilePath: ./Dockerfile
       dockerContext: .
       dockerCommand: streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0
       envVars:
         - key: OPENAI_API_KEY
           sync: false
         - key: API_URL
           fromService:
             name: patent-design-api
             type: web
             property: host
   ```

2. **Deploy via Render dashboard or CLI**

### AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04, t3.medium or larger)
2. **SSH into instance:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Follow Manual Server Setup above**

4. **Configure Security Groups:**
   - Allow HTTP (80) and HTTPS (443)
   - Allow SSH (22) from your IP

5. **Set up domain (optional):**
   - Point DNS to EC2 IP
   - Use Route 53 or your DNS provider

### DigitalOcean

1. **Create Droplet** (Ubuntu 22.04, 2GB RAM minimum)
2. **Follow Manual Server Setup above**
3. **Use DigitalOcean App Platform** for easier deployment:
   - Connect GitHub repository
   - Configure build settings
   - Set environment variables

### Heroku

1. **Install Heroku CLI:**
   ```bash
   heroku login
   ```

2. **Create apps:**
   ```bash
   heroku create patent-design-api
   heroku create patent-design-frontend
   ```

3. **Create `Procfile` for API:**
   ```
   web: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

4. **Create `Procfile` for Frontend:**
   ```
   web: streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **Set environment variables:**
   ```bash
   heroku config:set OPENAI_API_KEY=your-key -a patent-design-api
   heroku config:set OPENAI_API_KEY=your-key -a patent-design-frontend
   ```

## Environment Variables

Key environment variables to configure:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings/LLM | No* | - |
| `API_URL` | FastAPI backend URL | Yes | `http://localhost:8000` |
| `DATA_DIR` | Data directory path | No | `data` |
| `INDEX_DIR` | ChromaDB index directory | No | `data/index` |

*Required for full functionality; system works with local models if not provided

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change ports in docker-compose.yml or stop conflicting services
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Data directory permissions:**
   ```bash
   sudo chown -R $USER:$USER data/
   chmod -R 755 data/
   ```

3. **ChromaDB not found:**
   ```bash
   # Run ingestion first
   docker-compose run api python ingest.py
   ```

4. **Memory issues:**
   - Increase Docker memory allocation
   - Use smaller models (all-MiniLM-L6-v2 instead of text-embedding-3-large)
   - Reduce number of patents indexed

5. **Connection timeout:**
   - Check firewall settings
   - Verify API_URL matches actual backend URL
   - Check CORS settings in app.py

### Logs

View logs for debugging:
```bash
# Docker Compose
docker-compose logs -f api
docker-compose logs -f frontend

# Individual containers
docker logs patent-design-api
docker logs patent-design-frontend
```

### Health Checks

Check API health:
```bash
curl http://localhost:8000/health
```

Check API documentation:
```bash
# Open in browser
http://localhost:8000/docs
```

## Performance Optimization

1. **Use production WSGI server:**
   ```bash
   # Install gunicorn
   pip install gunicorn
   
   # Update command in docker-compose
   command: gunicorn app:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

2. **Enable caching:**
   - Use Redis for caching embeddings
   - Cache frequently accessed patents

3. **Database optimization:**
   - Use PostgreSQL for metadata
   - Optimize ChromaDB index settings

4. **CDN for static files:**
   - Serve media files via CDN
   - Cache API responses

## Security Considerations

1. **Set strong environment variables:**
   - Never commit `.env` file
   - Use secrets management in production

2. **Enable HTTPS:**
   - Use Let's Encrypt for free SSL
   - Configure nginx with SSL

3. **Rate limiting:**
   - Add rate limiting to API endpoints
   - Use API keys for authentication

4. **CORS configuration:**
   - Restrict CORS origins in production
   - Update `allow_origins` in app.py

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review documentation in README.md
- Open an issue on GitHub

