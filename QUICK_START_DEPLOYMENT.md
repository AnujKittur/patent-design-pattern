# Quick Start: Deploy Patent Design Pattern System

## Quick Deployment (Docker Compose)

### 1. One-Command Setup
```bash
./deploy.sh
```

This script will:
- Check prerequisites (Docker, Docker Compose)
- Create `.env` file if needed
- Create data directories
- Optionally run patent ingestion
- Build and start all services

### 2. Manual Setup

**Step 1: Set up environment**
```bash
cp .env.example .env
# Edit .env and add OPENAI_API_KEY if you have one
```

**Step 2: Start services**
```bash
docker-compose up --build
```

**Step 3: Access the application**
- Frontend: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Production Deployment

**With Nginx reverse proxy:**
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

Access via:
- Frontend: http://your-domain/
- API: http://your-domain/api/

## Cloud Deployments

### Railway.app
```bash
railway init
railway up
```

### Render.com
1. Connect GitHub repository
2. Render will auto-detect `render.yaml`
3. Set environment variables in dashboard

### AWS EC2 / DigitalOcean
1. SSH into server
2. Clone repository
3. Run `./deploy.sh`

## Important Notes

1. **First Time Setup**: Run patent ingestion before using:
   ```bash
   docker-compose run api python ingest.py
   ```

2. **Environment Variables**: 
   - `OPENAI_API_KEY` is optional but recommended for best performance
   - `API_URL` should match your backend URL

3. **Data Persistence**: 
   - Data is stored in `./data/` directory
   - Make sure to backup this directory

4. **Ports**:
   - API: 8000
   - Frontend: 8501
   - Nginx (production): 80

## Troubleshooting

**Services won't start:**
```bash
docker-compose logs -f
```

**Check health:**
```bash
curl http://localhost:8000/health
```

**Restart services:**
```bash
docker-compose restart
```

**Stop services:**
```bash
docker-compose down
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

