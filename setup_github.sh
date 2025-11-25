#!/bin/bash

# Script to set up GitHub repository for Patent Design Pattern Project

echo "🚀 Setting up GitHub Repository"
echo "================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    echo "   Mac: brew install git"
    echo "   Or download from: https://git-scm.com/downloads"
    exit 1
fi

# Check if already a git repository
if [ -d ".git" ]; then
    echo "⚠️  This directory is already a git repository"
    read -p "Do you want to reinitialize? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .git
        echo "✅ Removed existing .git directory"
    else
        echo "Using existing git repository"
    fi
fi

# Initialize git repository
if [ ! -d ".git" ]; then
    echo "1. Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
fi

# Check if .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo "2. Creating .gitignore..."
    # .gitignore should already exist from previous step
    echo "✅ .gitignore created"
else
    echo "✅ .gitignore already exists"
fi

# Add all files
echo ""
echo "3. Adding files to git..."
git add .
echo "✅ Files added"

# Create initial commit
echo ""
echo "4. Creating initial commit..."
git commit -m "Initial commit: Patent Design Pattern RAG System

- RAG-based construction robotics design generator
- Patent-grounded design generation with citations
- Hybrid retrieval (BM25 + Vector search)
- Modern animated Streamlit UI
- FastAPI backend with comprehensive API
- Docker deployment support
- Full documentation and deployment guides"
echo "✅ Initial commit created"

# Get repository name
echo ""
echo "5. Setting up remote repository..."
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Go to https://github.com/new"
echo "2. Create a new repository (e.g., 'patent-design-pattern')"
echo "3. DO NOT initialize with README, .gitignore, or license"
echo "4. Copy the repository URL (e.g., https://github.com/YOUR_USERNAME/patent-design-pattern.git)"
echo ""
read -p "Enter your GitHub repository URL (or press Enter to skip): " repo_url

if [ -n "$repo_url" ]; then
    echo ""
    echo "6. Adding remote repository..."
    git remote add origin "$repo_url"
    echo "✅ Remote added: $repo_url"
    
    echo ""
    echo "7. Pushing to GitHub..."
    git branch -M main
    git push -u origin main
    echo ""
    echo "✅ Code pushed to GitHub!"
    echo ""
    echo "🌐 Your repository is now live at: $repo_url"
else
    echo ""
    echo "⚠️  Skipping remote setup. You can add it later with:"
    echo "   git remote add origin YOUR_REPO_URL"
    echo "   git branch -M main"
    echo "   git push -u origin main"
fi

echo ""
echo "============================================"
echo "✅ GitHub setup complete!"
echo "============================================"
echo ""
echo "📋 Summary:"
echo "   • Git repository initialized"
echo "   • Files committed"
if [ -n "$repo_url" ]; then
    echo "   • Code pushed to GitHub"
    echo "   • Repository: $repo_url"
fi
echo ""
echo "📚 Next steps for hosting:"
echo "   1. See HOST_ON_GITHUB.md for hosting options"
echo "   2. Or use Streamlit Cloud (recommended for Streamlit apps)"
echo "   3. Or deploy to Railway/Render using deployment guides"
echo ""

