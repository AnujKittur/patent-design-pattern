# Hosting Your Website on GitHub

Since GitHub Pages doesn't directly support Streamlit apps, here are the best options:

## 🎯 Recommended: Streamlit Cloud (Free & Easy)

**Best option for Streamlit apps!**

### Steps:

1. **Push your code to GitHub** (use `setup_github.sh`)

2. **Go to Streamlit Cloud**: https://share.streamlit.io/

3. **Sign in with GitHub**

4. **Click "New app"**

5. **Select your repository**

6. **Configure:**
   - **Main file path**: `streamlit_app.py`
   - **Python version**: 3.11
   - **Branch**: `main`

7. **Add secrets** (if needed):
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `API_URL`: Your backend API URL (or use Streamlit Cloud's internal networking)

8. **Deploy!**

Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

---

## Option 2: GitHub Actions + Railway/Render

### Using GitHub Actions to Deploy

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        uses: bervProject/railway-deploy@master
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: your-service-name
```

---

## Option 3: GitHub Pages (Static Site)

If you want to create a static documentation site:

1. **Create a docs folder** with static HTML
2. **Enable GitHub Pages** in repository settings
3. **Select docs folder** as source

---

## Option 4: Manual Deployment Script

Use the deployment scripts provided:

```bash
# Deploy to Railway
railway login
railway init
railway up

# Deploy to Render
# Connect GitHub repo in Render dashboard
# Render will auto-detect render.yaml
```

---

## 🚀 Quick Setup Guide

### Step 1: Push to GitHub

```bash
# Run the setup script
./setup_github.sh

# Or manually:
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Choose Hosting Platform

**For Streamlit apps:**
- ✅ **Streamlit Cloud** (Recommended - Free, Easy)
- ✅ **Railway.app** (Free tier available)
- ✅ **Render.com** (Free tier available)

**For API + Frontend:**
- ✅ **Railway.app** (Supports multiple services)
- ✅ **Render.com** (Multiple services)
- ✅ **AWS/DigitalOcean** (More control)

### Step 3: Deploy

**Streamlit Cloud:**
1. Go to https://share.streamlit.io/
2. Connect GitHub repo
3. Deploy!

**Railway:**
```bash
railway login
railway init
railway up
```

**Render:**
1. Go to https://render.com
2. Connect GitHub
3. Create Web Service
4. Use `render.yaml` config

---

## 📝 Environment Variables

When deploying, make sure to set:

- `OPENAI_API_KEY` (optional but recommended)
- `API_URL` (if using separate API service)
- `DATA_DIR` (default: `data`)
- `INDEX_DIR` (default: `data/index`)

---

## 🔗 Useful Links

- [Streamlit Cloud](https://share.streamlit.io/)
- [Railway.app](https://railway.app/)
- [Render.com](https://render.com/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

---

## 💡 Pro Tips

1. **Use Streamlit Cloud** for easiest deployment
2. **Keep data in GitHub** (small files) or use external storage
3. **Use secrets** for API keys (never commit them!)
4. **Set up CI/CD** with GitHub Actions for auto-deployment
5. **Monitor** your app with platform's monitoring tools

---

## 🆘 Troubleshooting

**App won't start:**
- Check environment variables are set
- Verify `requirements.txt` is complete
- Check logs in deployment platform

**API connection issues:**
- Ensure API_URL is correct
- Check CORS settings in `app.py`
- Verify both services are deployed

**Data not loading:**
- Run `python ingest.py` before deploying
- Or include data in repository (if small)
- Or use external storage (S3, etc.)

---

**Need help?** Check the main [DEPLOYMENT.md](DEPLOYMENT.md) guide!

