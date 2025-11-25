# How to Run setup_github.sh - Step by Step Guide

## 📍 Where to Run It

You need to run this in your **Terminal** (command line) on your Mac.

---

## 🚀 Method 1: Using Terminal (Easiest)

### Step 1: Open Terminal

**Option A: Using Spotlight**
1. Press `Cmd + Space` (Command key + Spacebar)
2. Type: `Terminal`
3. Press `Enter`

**Option B: Using Finder**
1. Open **Finder**
2. Go to **Applications** → **Utilities**
3. Double-click **Terminal**

### Step 2: Navigate to Your Project

In the Terminal window, type:

```bash
cd /Users/anuj_kittur/Desktop/Scraper
```

Press `Enter`

You should see something like:
```
anuj_kittur@MacBook Scraper %
```

### Step 3: Run the Script

Type this command:

```bash
./setup_github.sh
```

Press `Enter`

---

## 🖱️ Method 2: Using Finder (Visual)

### Step 1: Open Finder

1. Open **Finder**
2. Navigate to: `Desktop` → `Scraper`

### Step 2: Open Terminal from Finder

1. Right-click on the `Scraper` folder
2. Select **"New Terminal at Folder"** (or "Services" → "New Terminal at Folder")

This opens Terminal already in the correct directory!

### Step 3: Run the Script

Type:

```bash
./setup_github.sh
```

Press `Enter`

---

## 🔍 Method 3: Drag and Drop (Easiest for Beginners)

### Step 1: Open Terminal

Press `Cmd + Space`, type `Terminal`, press `Enter`

### Step 2: Type the Command (Don't Press Enter Yet)

```bash
cd 
```

(Leave a space after `cd`)

### Step 3: Drag the Folder

1. Open **Finder**
2. Navigate to `Desktop` → `Scraper`
3. **Drag the `Scraper` folder** into the Terminal window
4. The path will automatically appear!
5. Press `Enter`

### Step 4: Run the Script

```bash
./setup_github.sh
```

Press `Enter`

---

## ✅ What You Should See

When you run the script, you'll see:

```
🚀 Setting up GitHub Repository
================================

1. Initializing git repository...
✅ Git repository initialized

2. Creating .gitignore...
✅ .gitignore created

3. Adding files to git...
✅ Files added

4. Creating initial commit...
✅ Initial commit created

5. Setting up remote repository...

📝 Next steps:
...
```

---

## 🆘 Troubleshooting

### "Permission denied" Error

If you see:
```
bash: ./setup_github.sh: Permission denied
```

**Fix it:**
```bash
chmod +x setup_github.sh
./setup_github.sh
```

### "Command not found" Error

If you see:
```
bash: ./setup_github.sh: No such file or directory
```

**Check you're in the right directory:**
```bash
pwd
```

Should show: `/Users/anuj_kittur/Desktop/Scraper`

If not, run:
```bash
cd /Users/anuj_kittur/Desktop/Scraper
```

### "Git is not installed"

If you see:
```
❌ Git is not installed
```

**Install Git:**
```bash
# Mac - using Homebrew
brew install git

# Or download from: https://git-scm.com/downloads
```

---

## 📝 Complete Example

Here's what a complete session looks like:

```bash
# Open Terminal, then:

anuj_kittur@MacBook ~ % cd /Users/anuj_kittur/Desktop/Scraper
anuj_kittur@MacBook Scraper % ./setup_github.sh

🚀 Setting up GitHub Repository
================================

1. Initializing git repository...
✅ Git repository initialized
...
```

---

## 🎯 Quick Copy-Paste Commands

Just copy and paste these one by one:

```bash
cd /Users/anuj_kittur/Desktop/Scraper
```

```bash
chmod +x setup_github.sh
```

```bash
./setup_github.sh
```

---

## 💡 Pro Tip

You can also check if the script exists first:

```bash
ls -la setup_github.sh
```

If you see it listed, you're in the right place!

---

**Need more help?** The script will guide you through the rest of the process!

