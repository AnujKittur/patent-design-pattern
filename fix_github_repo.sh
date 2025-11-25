#!/bin/bash

# Fix GitHub repository - Remove wrong repo and set up correct one

echo "🔧 Fixing GitHub Repository Setup"
echo "=================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check current remote
echo "1. Checking current repository setup..."
if [ -d ".git" ]; then
    current_remote=$(git remote get-url origin 2>/dev/null || echo "none")
    echo "   Current remote: $current_remote"
    
    if [ "$current_remote" != "none" ]; then
        echo ""
        echo "⚠️  Found existing remote repository"
        read -p "Do you want to remove the current remote and set up a new one? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "   Removing current remote..."
            git remote remove origin 2>/dev/null
            echo "   ✅ Remote removed"
        else
            echo "   Keeping current remote"
        fi
    fi
else
    echo "   No git repository found. Initializing..."
    git init
    echo "   ✅ Git repository initialized"
fi

echo ""
echo "2. Checking files..."
if [ -f "streamlit_app.py" ] && [ -f "app.py" ]; then
    echo "   ✅ Patent project files found"
else
    echo "   ⚠️  Warning: Some project files may be missing"
fi

echo ""
echo "3. Adding files to git..."
git add .
echo "   ✅ Files staged"

echo ""
echo "4. Creating commit..."
git commit -m "Patent Design Pattern RAG System

- RAG-based construction robotics design generator
- Patent-grounded design generation with citations
- Hybrid retrieval (BM25 + Vector search)
- Modern animated Streamlit UI
- FastAPI backend
- Docker deployment support" 2>/dev/null || echo "   (No new changes to commit)"

echo ""
echo "============================================"
echo "✅ Repository is ready!"
echo "============================================"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Go to https://github.com/new"
echo "2. Create a NEW repository with name: 'patent-design-pattern'"
echo "3. DO NOT initialize with README, .gitignore, or license"
echo "4. Click 'Create repository'"
echo ""
echo "5. Copy the repository URL (it will look like):"
echo "   https://github.com/YOUR_USERNAME/patent-design-pattern.git"
echo ""
read -p "6. Paste your NEW repository URL here: " repo_url

if [ -n "$repo_url" ]; then
    echo ""
    echo "7. Setting up your repository..."
    
    # Remove old remote if exists
    git remote remove origin 2>/dev/null
    
    # Add new remote
    git remote add origin "$repo_url"
    echo "   ✅ Remote added: $repo_url"
    
    echo ""
    echo "8. Pushing to GitHub..."
    git branch -M main
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "============================================"
        echo "✅ SUCCESS! Your patent project is on GitHub!"
        echo "============================================"
        echo ""
        echo "🌐 Repository: $repo_url"
        echo ""
        echo "📋 What's included:"
        echo "   • Patent Design Pattern RAG System"
        echo "   • Streamlit UI with animations"
        echo "   • FastAPI backend"
        echo "   • All documentation"
        echo "   • Deployment scripts"
        echo ""
        echo "🚀 Next: Deploy to Streamlit Cloud"
        echo "   Go to: https://share.streamlit.io/"
        echo "   Connect your GitHub repo"
        echo "   Deploy!"
    else
        echo ""
        echo "⚠️  Push failed. Common issues:"
        echo "   • Repository doesn't exist yet"
        echo "   • Authentication required"
        echo "   • Wrong repository URL"
        echo ""
        echo "Try:"
        echo "   git push -u origin main"
    fi
else
    echo ""
    echo "⚠️  No URL provided. You can add it later with:"
    echo "   git remote add origin YOUR_REPO_URL"
    echo "   git branch -M main"
    echo "   git push -u origin main"
fi

echo ""

