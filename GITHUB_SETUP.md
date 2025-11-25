# 🚀 Quick Guide: Add Project to GitHub

## Step-by-Step Instructions

### Step 1: Run the Setup Script

```bash
cd /Users/anuj_kittur/Desktop/Scraper
./setup_github.sh
```

This will:
- ✅ Initialize git repository
- ✅ Add all files
- ✅ Create initial commit
- ✅ Help you connect to GitHub

### Step 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `patent-design-pattern` (or your choice)
3. Description: "RAG-based construction robotics design generator"
4. Choose: **Public** or **Private**
5. **DO NOT** check "Initialize with README"
6. Click **"Create repository"**

### Step 3: Connect and Push

When the script asks for repository URL, paste:
```
https://github.com/YOUR_USERNAME/patent-design-pattern.git
```

Or manually run:
```bash
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 4: Host Your Website

**Option A: Streamlit Cloud (Recommended)**
1. Go to: https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Main file: `streamlit_app.py`
6. Deploy!

**Option B: Railway/Render**
- See `HOST_ON_GITHUB.md` for details

## ✅ Done!

Your code is now on GitHub and ready to deploy!

**Repository URL**: https://github.com/YOUR_USERNAME/REPO_NAME

**Live Website**: https://YOUR_APP.streamlit.app (after Streamlit Cloud deployment)
