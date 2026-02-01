# GitHub Setup Guide

## Option 1: Using GitHub CLI (Recommended - Fastest)

### Install GitHub CLI (if not already installed)
```bash
brew install gh
```

### Authenticate with GitHub
```bash
gh auth login
```

### Create and Push Repository
```bash
cd /Users/evanforbes/Code/competitive-intelligence

# Create repository on GitHub and push
gh repo create competitive-intelligence --private --source=. --remote=origin --push

# Or if you want it public:
# gh repo create competitive-intelligence --public --source=. --remote=origin --push
```

That's it! Your repository is now on GitHub.

## Option 2: Manual Setup via GitHub Website

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `competitive-intelligence`
3. Description: "Automated competitive intelligence system for DFS/Prediction Market competitors"
4. Choose **Private** (recommended, contains API configurations)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 2: Add Remote and Push

GitHub will show you commands. Use these:

```bash
cd /Users/evanforbes/Code/competitive-intelligence

# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/competitive-intelligence.git

# Push to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Option 3: Using SSH (More Secure)

### Step 1: Set up SSH key (if you haven't)

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add key to SSH agent
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard
pbcopy < ~/.ssh/id_ed25519.pub
```

### Step 2: Add SSH key to GitHub

1. Go to https://github.com/settings/keys
2. Click "New SSH key"
3. Paste your key (already in clipboard)
4. Click "Add SSH key"

### Step 3: Create Repository and Push

```bash
cd /Users/evanforbes/Code/competitive-intelligence

# Create repo using GitHub CLI
gh repo create competitive-intelligence --private --source=. --remote=origin

# Or add remote manually with SSH
git remote add origin git@github.com:YOUR_USERNAME/competitive-intelligence.git

# Push to GitHub
git push -u origin main
```

## After Pushing to GitHub

### Clone to Another Machine

```bash
git clone https://github.com/YOUR_USERNAME/competitive-intelligence.git
cd competitive-intelligence
./scripts/setup.sh
# Add your .env file with API keys
```

### Access in Claude Code App

1. Open Claude Code app
2. Select "Open Folder" or "Clone Repository"
3. Navigate to or clone your GitHub repository
4. The full project will be available in Claude Code

### Update from Another Machine

```bash
cd /Users/evanforbes/Code/competitive-intelligence
git pull origin main
```

### Push Changes

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

## Important Security Notes

### Never Commit Secrets

The `.gitignore` already excludes:
- `.env` file (contains API keys)
- `venv/` directory
- Database files
- Log files

**Always verify before pushing:**
```bash
git status
# Make sure .env is not listed
```

### Sharing with Team

If sharing with others:

1. **Share repository URL** (they need GitHub access)
2. **DO NOT share `.env` file** via git
3. **Share API keys securely** (1Password, encrypted messaging, etc.)
4. Each team member creates their own `.env` from `.env.example`

### Repository Settings (if private)

To give team access:
1. Go to your repo on GitHub
2. Settings → Collaborators
3. Add team members by username/email

## Verify Everything

```bash
# Check remote is configured
git remote -v

# Should show:
# origin  https://github.com/YOUR_USERNAME/competitive-intelligence.git (fetch)
# origin  https://github.com/YOUR_USERNAME/competitive-intelligence.git (push)

# Check what's being tracked
git status

# Should show: nothing to commit, working tree clean
```

## Troubleshooting

### Authentication Failed

```bash
# Update credentials
gh auth login

# Or use personal access token
# Go to: https://github.com/settings/tokens
# Generate token with 'repo' permissions
# Use token as password when pushing
```

### Repository Already Exists

```bash
# Use the existing repo
git remote add origin https://github.com/YOUR_USERNAME/competitive-intelligence.git
git push -u origin main
```

### Permission Denied (SSH)

```bash
# Test SSH connection
ssh -T git@github.com

# Should see: "Hi YOUR_USERNAME! You've successfully authenticated"
# If not, check SSH key setup above
```

## Repository URL

After setup, your repository will be at:
```
https://github.com/YOUR_USERNAME/competitive-intelligence
```

Share this URL with anyone who needs access (make sure repo is public or they're added as collaborators).

## Using with Claude Code App

Once on GitHub:

### Method 1: Open Existing Local Project
1. Open Claude Code app
2. File → Open Folder
3. Navigate to `/Users/evanforbes/Code/competitive-intelligence`
4. Project loads with full context

### Method 2: Clone Fresh
1. Open Claude Code app
2. View → Command Palette → "Git: Clone"
3. Enter: `https://github.com/YOUR_USERNAME/competitive-intelligence`
4. Choose location
5. Open cloned folder

### Method 3: Using Claude Projects
1. In Claude Code, create a new project
2. Link to your local folder or clone from GitHub
3. All project context is maintained

## Continuous Deployment

For automatic deployment on push:

### GitHub Actions (Optional)

Create `.github/workflows/test.yml`:
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python3 scripts/verify_installation.py
```

This runs tests on every push to GitHub.

## Keep Repository Updated

```bash
# Regular workflow
git add .
git commit -m "Update configuration"
git push

# Pull latest changes
git pull

# View history
git log --oneline
```
