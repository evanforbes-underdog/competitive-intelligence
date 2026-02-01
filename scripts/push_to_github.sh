#!/bin/bash
# Push competitive intelligence project to GitHub

set -e

echo "========================================="
echo "Push to GitHub"
echo "========================================="

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Error: Git repository not initialized"
    exit 1
fi

# Configure git user if not set
if ! git config user.name > /dev/null 2>&1; then
    echo ""
    echo "Git user not configured. Let's set it up:"
    read -p "Enter your name: " username
    read -p "Enter your email: " useremail
    git config user.name "$username"
    git config user.email "$useremail"
    echo "Git user configured locally for this project"
fi

# Check if remote exists
if git remote | grep -q "origin"; then
    echo ""
    echo "Remote 'origin' already exists:"
    git remote -v
    echo ""
    read -p "Do you want to push to this remote? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "Aborted"
        exit 0
    fi
else
    echo ""
    echo "No remote repository configured yet."
    echo ""
    echo "Please create a repository on GitHub first:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: competitive-intelligence"
    echo "3. Make it PRIVATE (recommended - contains API configs)"
    echo "4. DO NOT initialize with README, .gitignore, or license"
    echo "5. Click 'Create repository'"
    echo ""
    read -p "Enter your GitHub username: " github_user
    echo ""
    echo "Choose connection method:"
    echo "1. HTTPS (easier, uses token/password)"
    echo "2. SSH (more secure, requires SSH key setup)"
    read -p "Enter choice (1 or 2): " method

    if [ "$method" == "2" ]; then
        remote_url="git@github.com:${github_user}/competitive-intelligence.git"
    else
        remote_url="https://github.com/${github_user}/competitive-intelligence.git"
    fi

    echo ""
    echo "Adding remote: $remote_url"
    git remote add origin "$remote_url"
fi

# Show what will be pushed
echo ""
echo "Current commits to be pushed:"
git log --oneline
echo ""

# Verify .env is not being committed
if git ls-files | grep -q "^\.env$"; then
    echo "ERROR: .env file is tracked by git!"
    echo "This file contains API keys and should NOT be committed."
    echo ""
    echo "Run this to fix:"
    echo "  git rm --cached .env"
    echo "  git commit -m 'Remove .env from tracking'"
    exit 1
fi

echo "✓ .env file is not tracked (good!)"
echo ""

# Push to GitHub
echo "Pushing to GitHub..."
if git push -u origin main; then
    echo ""
    echo "========================================="
    echo "✓ Successfully pushed to GitHub!"
    echo "========================================="
    echo ""
    echo "Your repository is now available at:"
    git remote get-url origin | sed 's/git@github.com:/https:\/\/github.com\//' | sed 's/\.git$//'
    echo ""
    echo "Next steps:"
    echo "1. Access the repository in Claude Code app"
    echo "2. Clone on another machine: git clone <repository-url>"
    echo "3. Share with team (add collaborators on GitHub)"
    echo ""
    echo "IMPORTANT: Never commit your .env file!"
    echo "Team members should create their own .env from .env.example"
else
    echo ""
    echo "Push failed. Common issues:"
    echo ""
    echo "1. Repository doesn't exist on GitHub"
    echo "   → Create it first at https://github.com/new"
    echo ""
    echo "2. Authentication failed (HTTPS)"
    echo "   → Use a personal access token as password"
    echo "   → Generate at: https://github.com/settings/tokens"
    echo "   → Needs 'repo' permission"
    echo ""
    echo "3. Permission denied (SSH)"
    echo "   → Set up SSH key: ssh-keygen -t ed25519 -C 'your-email@example.com'"
    echo "   → Add to GitHub: https://github.com/settings/keys"
    echo ""
    echo "See GITHUB_SETUP.md for detailed instructions"
    exit 1
fi
