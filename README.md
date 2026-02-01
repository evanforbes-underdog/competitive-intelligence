# Competitive Intelligence Automation System

An automated system that monitors DFS and Prediction Market competitors, collecting news and generating weekly intelligence reports.

## Overview

This system runs weekly (Monday at 8am) to:
- Collect news from NewsAPI, industry websites, and app stores
- Summarize and categorize articles using Claude AI
- Generate executive summaries highlighting key developments
- Email HTML reports to stakeholders

## Competitors Tracked

- **High Priority**: PrizePicks, FanDuel, DraftKings, Kalshi
- **Medium Priority**: Robinhood, Betr, Fanatics
- **Low Priority**: BetMGM

## Features

- **Multi-Source Collection**: NewsAPI, web scraping, app store data
- **AI-Powered Analysis**: Claude API for intelligent summarization
- **Smart Deduplication**: Content-based hashing prevents duplicate articles
- **Executive Summaries**: Automatically highlights most important news
- **Graceful Degradation**: System continues even if some sources fail
- **Cost-Optimized**: Batch processing keeps Claude API costs under $4/month

## Quick Start

1. **Clone and Setup**
   ```bash
   cd /Users/evanforbes/Code/competitive-intelligence
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

2. **Configure API Keys**

   Edit `.env` file with your credentials:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-xxx
   NEWSAPI_KEY=your_newsapi_key
   GMAIL_USERNAME=your-email@gmail.com
   GMAIL_APP_PASSWORD=your_app_password
   ```

3. **Test Configuration**
   ```bash
   python3 scripts/test_email.py
   ```

4. **Run Manual Test**
   ```bash
   python3 scripts/manual_run.py
   ```

5. **Schedule Automated Runs**
   ```bash
   crontab -e
   # Add this line:
   0 8 * * 1 /Users/evanforbes/Code/competitive-intelligence/venv/bin/python3 /Users/evanforbes/Code/competitive-intelligence/src/main.py
   ```

## Project Structure

```
competitive-intelligence/
├── config/
│   └── config.yaml              # Main configuration
├── src/
│   ├── main.py                  # Main orchestrator
│   ├── collectors/              # Data collection modules
│   ├── processors/              # AI processing (summarize, categorize)
│   ├── database/                # SQLite models and repository
│   ├── reporting/               # Report generation and email
│   └── utils/                   # Utilities (logging, config, etc.)
├── scripts/
│   ├── setup.sh                 # Initial setup
│   ├── test_email.py            # Test email configuration
│   └── manual_run.py            # Manual test run
├── data/
│   ├── competitive_intel.db     # SQLite database
│   └── logs/                    # Log files
└── docs/                        # Additional documentation
```

## Configuration

Edit `config/config.yaml` to:
- Add/remove competitors
- Adjust lookback period (default: 7 days)
- Configure data sources
- Modify email recipients
- Tune AI parameters

See [CONFIGURATION.md](docs/CONFIGURATION.md) for details.

## API Requirements

1. **Anthropic API** (Claude): For AI summarization
   - Sign up: https://console.anthropic.com/
   - Cost: ~$3-4/month with batch processing

2. **NewsAPI.org**: For news collection
   - Sign up: https://newsapi.org/
   - Free tier: 100 requests/day (sufficient)

3. **Gmail App Password**: For email delivery
   - Enable 2FA on your Google account
   - Generate app password: https://myaccount.google.com/apppasswords

## Usage

### Manual Run
```bash
# Activate virtual environment
source venv/bin/activate

# Run manually (saves report to file, doesn't send email)
python3 scripts/manual_run.py

# Run full pipeline (including email)
python3 src/main.py
```

### Scheduled Run
The cron job automatically runs every Monday at 8am:
```bash
0 8 * * 1 /path/to/venv/bin/python3 /path/to/src/main.py
```

### Testing
```bash
# Test email configuration
python3 scripts/test_email.py

# Check logs
tail -f data/logs/competitive_intel.log

# View database
sqlite3 data/competitive_intel.db
```

## Monitoring

- **Logs**: Check `data/logs/competitive_intel.log`
- **Database**: Query `execution_logs` table for run history
- **Reports**: Saved to `data/reports/` if email fails

## Troubleshooting

### Email Not Sending
- Verify Gmail credentials in `.env`
- Ensure 2FA is enabled and app password is used
- Check firewall allows SMTP connections

### No Articles Collected
- Verify API keys are valid
- Check lookback period (may need to increase)
- Review logs for collector errors

### Claude API Errors
- Verify API key is correct
- Check rate limits (50 requests/minute)
- System falls back to extractive summarization if API fails

## Cost Breakdown

- **Claude API**: $0.90/week (~$3.60/month)
  - Batch processing optimizes token usage
  - Falls back to extractive summarization if needed

- **NewsAPI**: Free (well under 100 requests/day limit)

- **Total**: ~$3.60/month

## Future Enhancements

- Slack integration for instant notifications
- Web dashboard for browsing historical data
- Sentiment analysis
- Social media monitoring
- Custom alerts for specific events

## License

Internal use only.

## Support

For issues or questions, check:
- Logs: `data/logs/competitive_intel.log`
- Documentation: `docs/` directory
- Database: Query `execution_logs` table
