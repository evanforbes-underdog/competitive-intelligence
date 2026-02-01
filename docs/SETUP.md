# Setup Guide

Detailed setup instructions for the Competitive Intelligence System.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Active internet connection
- Gmail account (for sending reports)

## Installation Steps

### 1. Clone/Navigate to Project

```bash
cd /Users/evanforbes/Code/competitive-intelligence
```

### 2. Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This script will:
- Create a Python virtual environment
- Install all dependencies
- Create `.env` file from template
- Initialize the SQLite database
- Set up data directories

### 3. Configure API Keys

Edit the `.env` file:

```bash
nano .env  # or use your preferred editor
```

Required variables:

```bash
# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-xxx

# NewsAPI Key
NEWSAPI_KEY=your_newsapi_key_here

# Gmail Credentials
GMAIL_USERNAME=your-email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here

# Environment
ENVIRONMENT=production
```

### 4. Obtain API Keys

#### Anthropic API (Claude)

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)
6. Paste into `.env` file

#### NewsAPI

1. Go to https://newsapi.org/
2. Sign up for free account
3. Get your API key from dashboard
4. Paste into `.env` file

Free tier includes:
- 100 requests per day
- 7 days of historical data
- Perfect for this use case (8-10 requests per week)

#### Gmail App Password

1. Enable 2-Factor Authentication on your Google account:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. Generate App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Click "Generate"
   - Copy the 16-character password (remove spaces)
   - Paste into `.env` file as `GMAIL_APP_PASSWORD`

**Important**: Use the app password, NOT your regular Gmail password!

### 5. Configure Recipients

Edit `config/config.yaml`:

```yaml
reporting:
  email:
    recipients:
      - your-email@example.com
      - colleague@example.com
```

Add all email addresses that should receive reports.

### 6. Test Configuration

#### Test Email Sending

```bash
python3 scripts/test_email.py
```

This verifies:
- Configuration loads correctly
- Gmail credentials work
- SMTP connection succeeds
- Test email is sent

Expected output:
```
Email Configuration Test
========================================
1. Loading configuration...
   ✓ Configuration loaded
2. Checking email credentials...
   ✓ Gmail username: your-email@gmail.com
3. Initializing email sender...
   ✓ Email sender initialized
4. Testing SMTP connection...
   ✓ SMTP connection successful
5. Sending test email...
   ✓ Test email sent to your-email@example.com
========================================
All tests passed! Email configuration is working.
```

### 7. Test Data Collection

Run a manual test to collect articles:

```bash
python3 scripts/manual_run.py
```

This will:
- Collect articles from all sources
- Store in database
- Generate summaries with Claude
- Create HTML report
- Save report to `data/reports/` (without sending email)

First run may take 5-10 minutes depending on article volume.

### 8. Set Up Automated Schedule

#### Using Cron (macOS/Linux)

1. Open crontab editor:
   ```bash
   crontab -e
   ```

2. Add this line (runs every Monday at 8am):
   ```bash
   0 8 * * 1 /Users/evanforbes/Code/competitive-intelligence/venv/bin/python3 /Users/evanforbes/Code/competitive-intelligence/src/main.py
   ```

3. Save and exit

4. Verify cron job:
   ```bash
   crontab -l
   ```

#### Cron Schedule Examples

```bash
# Every Monday at 8am
0 8 * * 1 /path/to/venv/bin/python3 /path/to/src/main.py

# Every day at 9am
0 9 * * * /path/to/venv/bin/python3 /path/to/src/main.py

# Every weekday at 8am
0 8 * * 1-5 /path/to/venv/bin/python3 /path/to/src/main.py

# Twice a week (Monday and Thursday at 8am)
0 8 * * 1,4 /path/to/venv/bin/python3 /path/to/src/main.py
```

## Verification Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] `.env` file configured with all API keys
- [ ] Recipients configured in `config.yaml`
- [ ] Email test passes
- [ ] Manual run completes successfully
- [ ] Report HTML generated and viewable
- [ ] Cron job configured (if using automation)
- [ ] First scheduled run completed successfully

## Directory Structure After Setup

```
competitive-intelligence/
├── venv/                        # Virtual environment
├── .env                         # API keys (DO NOT COMMIT)
├── data/
│   ├── competitive_intel.db     # SQLite database
│   ├── logs/
│   │   └── competitive_intel.log
│   └── reports/
│       └── manual_report_*.html
```

## Troubleshooting Setup Issues

### Python Version Issues

```bash
# Check Python version
python3 --version

# Should be 3.8 or higher
# If not, install newer Python version
```

### Virtual Environment Activation Issues

```bash
# Make sure you're in the project directory
cd /Users/evanforbes/Code/competitive-intelligence

# Activate virtual environment
source venv/bin/activate

# Your prompt should show (venv)
```

### Dependency Installation Failures

```bash
# Upgrade pip first
pip install --upgrade pip

# Try installing requirements again
pip install -r requirements.txt

# If specific package fails, try installing separately
pip install anthropic==0.18.1
```

### Database Initialization Errors

```bash
# Manually initialize database
python3 src/database/migrations.py data/competitive_intel.db

# Check database was created
ls -lh data/competitive_intel.db
```

### Gmail Authentication Issues

Common issues:
- Using regular password instead of app password
- 2FA not enabled
- App password has spaces (remove them)
- "Less secure apps" setting (no longer needed with app passwords)

Solution:
1. Enable 2FA on Google account
2. Generate new app password
3. Use 16-character password without spaces

### Cron Job Not Running

```bash
# Check cron service is running
# macOS:
launchctl list | grep cron

# Linux:
service cron status

# View cron logs
# macOS:
tail -f /var/log/system.log | grep cron

# Linux:
tail -f /var/log/syslog | grep CRON

# Test cron command manually
/Users/evanforbes/Code/competitive-intelligence/venv/bin/python3 /Users/evanforbes/Code/competitive-intelligence/src/main.py
```

## Next Steps

After successful setup:
1. Monitor first scheduled run
2. Review report quality
3. Adjust configuration as needed (competitors, sources, etc.)
4. Set up monitoring/alerts for failures
5. Consider cost optimization if Claude usage is high

See [CONFIGURATION.md](CONFIGURATION.md) for configuration options.
