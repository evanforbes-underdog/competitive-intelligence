# Quick Start Guide

Get the Competitive Intelligence System running in 15 minutes.

## Prerequisites

- Python 3.8+
- Gmail account
- API keys ready (or sign up during setup)

## Step-by-Step Setup

### 1. Run Setup Script (2 minutes)

```bash
cd /Users/evanforbes/Code/competitive-intelligence
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This creates virtual environment, installs dependencies, and initializes database.

### 2. Get API Keys (5 minutes)

#### Anthropic API (Claude)
1. Visit https://console.anthropic.com/
2. Sign up / Log in
3. Navigate to "API Keys"
4. Create new key
5. Copy key (starts with `sk-ant-`)

#### NewsAPI
1. Visit https://newsapi.org/
2. Sign up (free tier is fine)
3. Copy API key from dashboard

#### Gmail App Password
1. Enable 2FA on Google account: https://myaccount.google.com/security
2. Generate app password: https://myaccount.google.com/apppasswords
3. Copy 16-character password (remove spaces)

### 3. Configure Keys (2 minutes)

```bash
# Edit .env file
nano .env
```

Paste your keys:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
NEWSAPI_KEY=your-newsapi-key
GMAIL_USERNAME=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
ENVIRONMENT=production
```

Save and exit (Ctrl+X, Y, Enter).

### 4. Configure Recipients (1 minute)

```bash
# Edit config file
nano config/config.yaml
```

Update recipients:
```yaml
reporting:
  email:
    recipients:
      - your-email@example.com
      - colleague@example.com
```

Save and exit.

### 5. Test Email (1 minute)

```bash
source venv/bin/activate
python3 scripts/test_email.py
```

Expected output:
```
✓ Configuration loaded
✓ Gmail username: your-email@gmail.com
✓ Email sender initialized
✓ SMTP connection successful
✓ Test email sent
```

### 6. Test Collection (5 minutes)

```bash
python3 scripts/manual_run.py
```

This will:
- Collect articles from all sources
- Generate AI summaries
- Create HTML report (saved to `data/reports/`)
- NOT send email

Check the output for errors. Review the generated HTML report.

### 7. Schedule Automation (1 minute)

```bash
crontab -e
```

Add this line (runs every Monday at 8am):
```bash
0 8 * * 1 /Users/evanforbes/Code/competitive-intelligence/venv/bin/python3 /Users/evanforbes/Code/competitive-intelligence/src/main.py
```

Save and exit.

### 8. Done! 🎉

The system is now configured and will run automatically every Monday at 8am.

## Verification

After first scheduled run:
- Check email for report
- Review logs: `tail -f data/logs/competitive_intel.log`
- Query database: `sqlite3 data/competitive_intel.db "SELECT * FROM execution_logs;"`

## Common Issues

### Email test fails
- Verify 2FA is enabled on Google account
- Use app password, not regular password
- Remove spaces from app password
- Check Gmail allows SMTP access

### No articles collected
- Verify API keys are correct
- Check internet connection
- Review logs for specific errors
- Try increasing `lookback_days` in config

### Claude API errors
- Verify API key starts with `sk-ant-`
- Check account has credits
- System will fall back to extractive summaries if needed

## Daily Usage

### View Latest Report
```bash
open data/reports/report_*.html
```

### Check Logs
```bash
tail -f data/logs/competitive_intel.log
```

### Manual Run
```bash
source venv/bin/activate
python3 scripts/manual_run.py
```

### Full Pipeline (with email)
```bash
source venv/bin/activate
python3 src/main.py
```

## Configuration Changes

### Add Competitor
Edit `config/config.yaml`:
```yaml
competitors:
  - name: NewCompetitor
    keywords: ["new competitor", "newcomp"]
    priority: high
```

### Change Schedule
```bash
crontab -e
```

Examples:
```bash
# Daily at 9am
0 9 * * * /path/to/venv/bin/python3 /path/to/src/main.py

# Monday and Thursday at 8am
0 8 * * 1,4 /path/to/venv/bin/python3 /path/to/src/main.py
```

### Change Recipients
Edit `config/config.yaml`:
```yaml
reporting:
  email:
    recipients:
      - new-email@example.com
```

## Monitoring

### Check Cron Job
```bash
crontab -l
```

### View Execution History
```bash
sqlite3 data/competitive_intel.db
SELECT run_date, status, articles_collected, articles_new FROM execution_logs ORDER BY run_date DESC LIMIT 10;
.quit
```

### Database Stats
```bash
sqlite3 data/competitive_intel.db
SELECT competitor, COUNT(*) as count FROM articles GROUP BY competitor;
.quit
```

## Cost Tracking

Monitor Claude API usage:
1. Visit https://console.anthropic.com/
2. Check "Usage" section
3. Should be ~$0.90/week or $3.60/month

## Getting Help

1. Check logs: `data/logs/competitive_intel.log`
2. Review documentation: `docs/SETUP.md`, `docs/CONFIGURATION.md`
3. Run test scripts: `scripts/test_email.py`, `scripts/manual_run.py`
4. Check execution logs in database

## Full Documentation

- **README.md** - Project overview
- **docs/SETUP.md** - Detailed setup guide
- **docs/CONFIGURATION.md** - Configuration reference
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details

## Architecture Overview

```
Monday 8am
    ↓
Cron triggers main.py
    ↓
1. Collect articles (NewsAPI + Web + App Stores)
    ↓
2. Store in SQLite (deduplicate)
    ↓
3. Process with Claude API (summarize, categorize)
    ↓
4. Generate HTML report (with executive summary)
    ↓
5. Email via Gmail SMTP
    ↓
Done! (check inbox)
```

## Troubleshooting Commands

```bash
# Activate environment
source venv/bin/activate

# Test email
python3 scripts/test_email.py

# Manual run (no email)
python3 scripts/manual_run.py

# Full run (with email)
python3 src/main.py

# View logs
tail -f data/logs/competitive_intel.log

# Check database
sqlite3 data/competitive_intel.db
.tables
SELECT COUNT(*) FROM articles;
.quit

# Test cron command
/Users/evanforbes/Code/competitive-intelligence/venv/bin/python3 /Users/evanforbes/Code/competitive-intelligence/src/main.py

# View cron logs (macOS)
log show --predicate 'process == "cron"' --last 1h

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

After successful setup:
1. ✅ Wait for first scheduled run (Monday 8am)
2. ✅ Review report quality
3. ✅ Adjust configuration as needed
4. ✅ Add/remove competitors
5. ✅ Tune summary length, categories, etc.

Enjoy your automated competitive intelligence! 🚀
