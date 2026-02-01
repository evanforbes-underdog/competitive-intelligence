# Access in Claude Code App

## Quick Setup (3 Steps)

### Step 1: Create GitHub Repository (2 minutes)

1. Go to https://github.com/new
2. Repository name: **competitive-intelligence**
3. Make it **Private** (recommended - contains configuration)
4. **DO NOT** check any boxes (README, .gitignore, license)
5. Click **"Create repository"**

### Step 2: Push to GitHub (1 minute)

Run the helper script:
```bash
cd /Users/evanforbes/Code/competitive-intelligence
./scripts/push_to_github.sh
```

The script will:
- Configure git user if needed
- Ask for your GitHub username
- Set up the remote repository
- Push all code to GitHub
- Give you the repository URL

### Step 3: Access in Claude Code App (30 seconds)

**Option A: Open Existing Project**
1. Open Claude Code app
2. File → Open Folder
3. Select `/Users/evanforbes/Code/competitive-intelligence`
4. Done! Full project is available

**Option B: Clone Fresh**
1. Open Claude Code app
2. View → Command Palette (Cmd+Shift+P)
3. Type: "Git: Clone"
4. Paste your repository URL
5. Choose location
6. Open cloned folder

## That's It!

Your competitive intelligence system is now:
- ✅ Backed up on GitHub
- ✅ Accessible in Claude Code app anywhere
- ✅ Shareable with team members
- ✅ Version controlled

## Using Across Machines

### On Another Computer

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/competitive-intelligence.git
cd competitive-intelligence

# Set up the system
./scripts/setup.sh

# Add your API keys
cp .env.example .env
nano .env  # Add your keys

# Test it
python3 scripts/test_email.py
```

### Keep In Sync

```bash
# Pull latest changes
git pull

# Make changes and push
git add .
git commit -m "Updated configuration"
git push
```

## In Claude Code App

Once the project is open in Claude Code:

1. **Ask Claude to modify code**
   - "Add sentiment analysis to the summaries"
   - "Change the email template style"
   - "Add Twitter monitoring"

2. **Ask Claude to debug**
   - "Why are no articles being collected?"
   - "Fix the email sending error"
   - "Check the database schema"

3. **Ask Claude to explain**
   - "How does the deduplication work?"
   - "Explain the priority scoring algorithm"
   - "Show me how to add a new competitor"

4. **All project context is maintained**
   - Claude can see all files
   - Understands the architecture
   - Knows the configuration
   - Can make coordinated changes

## Sharing with Team

### Add Collaborators

1. Go to your repo: `https://github.com/YOUR_USERNAME/competitive-intelligence`
2. Settings → Collaborators
3. Add team members by username/email

### Team Setup

Team members:
1. Clone the repository
2. Run `./scripts/setup.sh`
3. Create their own `.env` file (you share keys securely)
4. Run `python3 scripts/test_email.py`

**IMPORTANT**: Never commit `.env` file - it's already in `.gitignore`

## Repository Structure on GitHub

Your repository includes:
- ✅ All source code
- ✅ Configuration templates
- ✅ Documentation
- ✅ Setup scripts
- ✅ Tests
- ❌ No `.env` file (kept local)
- ❌ No `venv/` (installed locally)
- ❌ No database (created on first run)
- ❌ No logs (generated at runtime)

## Troubleshooting

### Push Failed

**Authentication Error (HTTPS)**:
1. Create Personal Access Token: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Check "repo" permission
4. Copy token
5. Use token as password when pushing

**Permission Denied (SSH)**:
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your-email@example.com"`
2. Add to GitHub: https://github.com/settings/keys
3. Test: `ssh -T git@github.com`

### Repository Already Exists

If you already have a repo with that name, either:
- Delete the old repo on GitHub
- Or use a different name: `competitive-intelligence-v2`

### Claude Code Can't Find Project

Make sure:
1. Project folder exists on your machine
2. You have access to the GitHub repository
3. Claude Code has folder/file access permissions

## Advanced: GitHub Actions

Want to run tests on every push? Create `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python3 scripts/verify_installation.py
```

## Security Reminders

✅ **DO**:
- Keep repository private
- Use `.gitignore` (already configured)
- Share API keys through secure channels
- Add collaborators individually

❌ **DON'T**:
- Commit `.env` file
- Make repo public with sensitive configs
- Share tokens in repo issues/PRs
- Commit database files with data

## Next Steps

1. **Run the push script**: `./scripts/push_to_github.sh`
2. **Open in Claude Code**: File → Open Folder
3. **Start using**: Ask Claude to help with anything!

Your competitive intelligence system is now fully accessible in Claude Code! 🚀
