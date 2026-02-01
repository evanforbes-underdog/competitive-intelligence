# Deployment Checklist

Use this checklist to deploy the Competitive Intelligence System.

## Pre-Deployment

- [ ] Review system requirements
- [ ] Prepare API credentials (see below)
- [ ] Identify email recipients
- [ ] Review configuration settings

## API Credentials Needed

### 1. Anthropic API Key
- **Purpose**: Claude AI for article summarization
- **Sign up**: https://console.anthropic.com/
- **Cost**: ~$3.60/month with batch processing
- **Key format**: `sk-ant-...`

### 2. NewsAPI Key
- **Purpose**: News article collection
- **Sign up**: https://newsapi.org/
- **Cost**: Free (100 requests/day)
- **Key format**: 32-character hex string

### 3. Gmail Credentials
- **Purpose**: Email report delivery
- **Requirements**:
  - Gmail account with 2FA enabled
  - App password generated
- **Setup**: https://myaccount.google.com/apppasswords
- **Key format**: 16-character app password (remove spaces)

## Installation Steps

### 1. Run Setup Script
```bash
cd /Users/evanforbes/Code/competitive-intelligence
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Expected output:**
- Virtual environment created
- Dependencies installed
- Database initialized
- .env file created

**Time**: ~2 minutes

### 2. Configure API Keys

```bash
nano .env
```

Add your credentials:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
NEWSAPI_KEY=your-newsapi-key
GMAIL_USERNAME=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
ENVIRONMENT=production
```

Save and exit (Ctrl+X, Y, Enter).

**Time**: ~2 minutes

### 3. Configure Recipients

```bash
nano config/config.yaml
```

Update the recipients list:
```yaml
reporting:
  email:
    recipients:
      - primary@example.com
      - team-member@example.com
```

**Time**: ~1 minute

### 4. Verify Installation

```bash
source venv/bin/activate
python3 scripts/verify_installation.py
```

**Expected output:**
```
✓ Project structure
✓ Configuration files
✓ Python version
✓ Virtual environment exists
✓ All dependencies installed
✓ .env file exists
✓ Core source files
✓ Scripts are executable
✓ Database exists
✓ Email template exists

Verification Summary: 10/10 checks passed
✓ Installation looks good!
```

**Time**: ~30 seconds

- [ ] All checks passed

### 5. Test Email Configuration

```bash
python3 scripts/test_email.py
```

**Expected output:**
```
✓ Configuration loaded
✓ Gmail username: your-email@gmail.com
✓ Email sender initialized
✓ SMTP connection successful
✓ Test email sent to your-email@example.com

All tests passed! Email configuration is working.
```

**Time**: ~1 minute

- [ ] Test email received in inbox
- [ ] HTML rendering looks correct

### 6. Test Data Collection

```bash
python3 scripts/manual_run.py
```

**What happens:**
1. Collects articles from NewsAPI, web sources, app stores
2. Stores in database (with deduplication)
3. Generates summaries using Claude API
4. Creates HTML report
5. Saves to `data/reports/` (does NOT send email)

**Expected duration**: 5-10 minutes (first run)

**Expected output:**
```
Step 1: Collecting Articles
Collected X articles for PrizePicks
Collected Y articles for FanDuel
...

Step 2: Storing Articles
Stored N new articles (M duplicates skipped)

Step 3: Processing Articles
Summarizing N articles
Categorizing N articles
Prioritizing N articles

Step 4: Generating Report
✓ Report saved to: data/reports/manual_report_TIMESTAMP.html

Summary
Articles collected: X
New articles: N
Duplicates: M
Summaries generated: N
```

**Time**: ~5-10 minutes

- [ ] Articles collected (20+ expected for 7 days)
- [ ] No critical errors
- [ ] Report HTML generated
- [ ] Report renders correctly in browser

**Review the report:**
```bash
open data/reports/manual_report_*.html
```

Check:
- [ ] Executive summary shows top stories
- [ ] Articles grouped by competitor
- [ ] Summaries are relevant and concise
- [ ] Categories make sense
- [ ] Sources are listed

### 7. Set Up Automation

```bash
crontab -e
```

Add this line (runs every Monday at 8am):
```bash
0 8 * * 1 /Users/evanforbes/Code/competitive-intelligence/venv/bin/python3 /Users/evanforbes/Code/competitive-intelligence/src/main.py
```

Save and exit.

**Verify cron job:**
```bash
crontab -l
```

**Time**: ~2 minutes

- [ ] Cron job configured
- [ ] Schedule verified

### 8. Test Full Pipeline (Optional)

If you want to test the complete pipeline including email:

```bash
python3 src/main.py
```

This will:
1. Collect articles
2. Process with Claude
3. Generate report
4. **Send email to configured recipients**

**Warning**: This sends an actual email!

**Time**: ~5-10 minutes

- [ ] Email received by all recipients
- [ ] Report looks professional
- [ ] Executive summary is useful

## Post-Deployment

### Monitor First Scheduled Run

**When**: Next Monday at 8am

**Check:**
- [ ] Email received on time
- [ ] Report contains new articles
- [ ] No errors in logs
- [ ] All competitors represented

**View logs:**
```bash
tail -f data/logs/competitive_intel.log
```

### Week 1 Review

After first week of operation:

- [ ] Review report quality
- [ ] Check Claude API costs (~$0.90/week expected)
- [ ] Verify no duplicate articles
- [ ] Confirm all sources working
- [ ] Check execution logs for errors

**Check execution history:**
```bash
sqlite3 data/competitive_intel.db
SELECT run_date, status, articles_collected, articles_new, duration_seconds
FROM execution_logs
ORDER BY run_date DESC
LIMIT 5;
.quit
```

### Ongoing Monitoring

**Weekly:**
- [ ] Review Monday reports
- [ ] Check for errors in logs
- [ ] Verify all competitors represented

**Monthly:**
- [ ] Review Claude API costs
- [ ] Check database size
- [ ] Update competitors/sources as needed
- [ ] Review and tune configuration

**Quarterly:**
- [ ] Update dependencies: `pip install -r requirements.txt --upgrade`
- [ ] Review system performance
- [ ] Consider feature enhancements

## Troubleshooting

### Email Test Fails

**Symptoms**: SMTP connection error, authentication failed

**Solutions**:
1. Verify 2FA is enabled on Google account
2. Generate new app password
3. Use app password (not regular password)
4. Remove spaces from app password
5. Check Gmail allows SMTP access

**Test**:
```bash
python3 scripts/test_email.py
```

### No Articles Collected

**Symptoms**: "Collected 0 articles" in logs

**Solutions**:
1. Verify API keys are correct
2. Check internet connection
3. Increase `lookback_days` in config
4. Review specific collector errors in logs

**Test**:
```bash
python3 scripts/manual_run.py
```

### Claude API Errors

**Symptoms**: "Summarization failed" in logs

**Solutions**:
1. Verify API key starts with `sk-ant-`
2. Check account has credits
3. Review rate limits
4. System falls back to extractive summaries

**Note**: Extractive fallback is automatic, not an error

### Cron Job Not Running

**Symptoms**: No email on Monday morning

**Solutions**:
1. Check cron service is running
2. Verify cron job syntax
3. Test command manually
4. Check cron logs

**Verify cron job**:
```bash
crontab -l
```

**Test manually**:
```bash
/Users/evanforbes/Code/competitive-intelligence/venv/bin/python3 /Users/evanforbes/Code/competitive-intelligence/src/main.py
```

**Check cron logs** (macOS):
```bash
log show --predicate 'process == "cron"' --last 1h
```

## Success Criteria

The deployment is successful when:

- [x] All installation checks pass
- [x] Email test successful
- [x] Manual run collects 20+ articles
- [x] Report HTML renders correctly
- [x] Cron job configured
- [ ] First scheduled run completes (Monday 8am)
- [ ] Report received on schedule
- [ ] Claude API costs < $5/month
- [ ] No critical errors in logs

## Rollback Plan

If system encounters issues:

1. **Disable cron job temporarily**:
   ```bash
   crontab -e
   # Comment out the line with #
   ```

2. **Review logs**:
   ```bash
   tail -100 data/logs/competitive_intel.log
   ```

3. **Check database**:
   ```bash
   sqlite3 data/competitive_intel.db
   SELECT * FROM execution_logs ORDER BY run_date DESC LIMIT 1;
   .quit
   ```

4. **Fix issues and test manually**:
   ```bash
   python3 scripts/manual_run.py
   ```

5. **Re-enable cron job** when resolved

## Support Resources

- **Logs**: `data/logs/competitive_intel.log`
- **Documentation**:
  - `README.md` - Overview
  - `QUICK_START.md` - Quick reference
  - `docs/SETUP.md` - Detailed setup
  - `docs/CONFIGURATION.md` - Config reference
- **Database**: `data/competitive_intel.db`
- **Test Scripts**:
  - `scripts/verify_installation.py`
  - `scripts/test_email.py`
  - `scripts/manual_run.py`

## Final Checklist

Before marking deployment complete:

- [ ] All API keys configured
- [ ] Email test passed
- [ ] Manual run successful
- [ ] Report quality reviewed
- [ ] Cron job scheduled
- [ ] First automated run successful
- [ ] Team trained on monitoring
- [ ] Documentation reviewed

## Notes

**Date deployed**: _______________

**Deployed by**: _______________

**Initial recipients**: _______________

**Issues encountered**:

_______________________________________________

_______________________________________________

**Resolution**:

_______________________________________________

_______________________________________________

## Sign-off

- [ ] System deployed and operational
- [ ] Team notified
- [ ] Monitoring in place

**Signed**: _______________  **Date**: _______________
