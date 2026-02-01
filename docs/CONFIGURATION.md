# Configuration Guide

Detailed guide for configuring the Competitive Intelligence System.

## Configuration Files

- `config/config.yaml` - Main configuration
- `.env` - API keys and secrets (not committed to git)

## config.yaml Structure

### Competitors

Define competitors to track:

```yaml
competitors:
  - name: PrizePicks
    keywords: ["prizepicks", "prize picks"]
    ios_app_id: "1437391774"
    android_app_id: "com.prizepicks"
    priority: high
```

**Fields:**
- `name`: Display name for the competitor
- `keywords`: Search terms (used for NewsAPI and web scraping)
- `ios_app_id`: Apple App Store ID (optional)
- `android_app_id`: Google Play package name (optional)
- `priority`: `high`, `medium`, or `low` (affects prioritization)

**Adding a Competitor:**

```yaml
competitors:
  - name: NewCompetitor
    keywords: ["new competitor", "newcomp"]
    ios_app_id: "123456789"
    android_app_id: "com.newcompetitor.app"
    priority: medium
```

**Removing a Competitor:**

Simply delete or comment out the competitor entry.

### Collection Settings

```yaml
collection:
  lookback_days: 7                    # How many days of history to check
  max_articles_per_competitor: 50     # Limit per competitor
```

**lookback_days**: Increasing this will collect more articles but may increase processing time and API costs.

**Recommended values:**
- Weekly reports: 7 days
- Bi-weekly reports: 14 days
- Monthly reports: 30 days

### NewsAPI Configuration

```yaml
collection:
  newsapi:
    enabled: true
    max_requests_per_run: 10
    search_language: en
    sort_by: publishedAt
```

**enabled**: Set to `false` to disable NewsAPI collection

**max_requests_per_run**: Maximum API calls (8 competitors = 8 requests minimum)

**sort_by**: Options are `publishedAt`, `relevancy`, `popularity`

### Web Scraping

```yaml
collection:
  web_scraping:
    enabled: true
    sources:
      - name: SBC News
        url: "https://sbcnews.co.uk/sports-betting/"
        selector: "article.post"
```

**Adding a New Source:**

```yaml
sources:
  - name: Your News Site
    url: "https://example.com/news/"
    selector: "div.article"  # CSS selector for article elements
```

**Finding Selectors:**
1. Open the news site in browser
2. Right-click an article → Inspect
3. Find the HTML element that wraps articles
4. Use that element as the selector (e.g., `article`, `div.post`, etc.)

### App Stores

```yaml
collection:
  app_stores:
    enabled: true
    collect_reviews: false
    collect_ratings: true
```

**enabled**: Set to `false` to disable app store collection

**collect_reviews**: Currently not implemented (set to `false`)

**collect_ratings**: Collect rating information

### Claude AI Processing

```yaml
processing:
  claude:
    model: "claude-3-5-sonnet-20241022"
    max_tokens: 300
    temperature: 0.3
    batch_size: 10
```

**model**: Claude model to use
- `claude-3-5-sonnet-20241022` (recommended, balanced)
- `claude-3-haiku-20240307` (faster, cheaper, less detailed)
- `claude-3-opus-20240229` (more expensive, highest quality)

**max_tokens**: Maximum tokens per summary
- 300 = 2-3 sentences (recommended)
- 150 = 1-2 sentences (more concise)
- 500 = 3-5 sentences (more detailed)

**temperature**: Creativity level (0.0 - 1.0)
- 0.3 (recommended) - Focused, consistent
- 0.0 - Very deterministic
- 0.7 - More creative

**batch_size**: Articles processed per API call
- Higher = fewer API calls but longer prompts
- 10 is optimal for most cases
- Cost = (tokens / 1M) × price

### Categories

```yaml
processing:
  categories:
    - Product Updates
    - Marketing Campaigns
    - Partnerships
    - Regulatory News
    - Promotions
    - Executive Moves
    - Funding
    - Other
```

Articles are automatically categorized into these buckets. You can add custom categories:

```yaml
processing:
  categories:
    - Product Updates
    - Marketing Campaigns
    - User Growth
    - Technology Updates
    - Other
```

If adding categories, update keyword matching in `src/processors/categorizer.py`.

### Priority Weights

```yaml
processing:
  priority_weights:
    recency: 0.3
    source_authority: 0.25
    category_importance: 0.25
    competitor_priority: 0.2
```

These weights determine article priority scores (0-10):
- **recency**: Newer articles score higher
- **source_authority**: Bloomberg, Reuters score higher than blogs
- **category_importance**: Funding, Executive Moves score higher than Promotions
- **competitor_priority**: High priority competitors score higher

Weights must sum to 1.0.

**Example adjustment** (prioritize recency over source):
```yaml
priority_weights:
  recency: 0.4
  source_authority: 0.2
  category_importance: 0.25
  competitor_priority: 0.15
```

### Reporting

```yaml
reporting:
  email:
    recipients:
      - email1@example.com
      - email2@example.com
    subject: "Weekly Competitive Intelligence Report - {date}"
    from_name: "Competitive Intelligence Bot"
    include_executive_summary: true
    max_executive_items: 5
```

**recipients**: List of email addresses to receive reports

**subject**: Email subject (use `{date}` for automatic date insertion)

**max_executive_items**: Number of top stories in executive summary

**report_format**:
```yaml
report_format:
  group_by: competitor        # or "category"
  sort_by: priority          # or "date"
  include_metadata: true
```

### Rate Limits

```yaml
rate_limits:
  newsapi_requests_per_day: 100
  claude_requests_per_minute: 50
  web_scraping_delay_seconds: 2
```

**newsapi_requests_per_day**: Safety limit (NewsAPI free tier is 100)

**claude_requests_per_minute**: Anthropic rate limit

**web_scraping_delay_seconds**: Delay between web requests (be respectful)

### Logging

```yaml
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "data/logs/competitive_intel.log"
  max_bytes: 10485760    # 10MB
  backup_count: 5
```

**level**: Log verbosity
- `DEBUG` - Very verbose, for development
- `INFO` - Normal operation (recommended)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors

**max_bytes**: Log file size before rotation

**backup_count**: Number of old log files to keep

### Database

```yaml
database:
  path: "data/competitive_intel.db"
  cache_summaries_days: 30
```

**path**: SQLite database location (relative to project root)

**cache_summaries_days**: How long to cache summaries (prevents re-processing)

## Environment Variables (.env)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx
NEWSAPI_KEY=your_key
GMAIL_USERNAME=your-email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# Optional
ENVIRONMENT=production
CONFIG_PATH=/custom/path/to/config.yaml
```

**ANTHROPIC_API_KEY**: Claude API key from https://console.anthropic.com/

**NEWSAPI_KEY**: NewsAPI key from https://newsapi.org/

**GMAIL_USERNAME**: Gmail address for sending reports

**GMAIL_APP_PASSWORD**: Gmail app password (not regular password!)

**ENVIRONMENT**: `production` or `development`

**CONFIG_PATH**: Optional custom config file location

## Configuration Best Practices

### For Weekly Reports
```yaml
lookback_days: 7
max_executive_items: 5
batch_size: 10
```

### For Daily Reports
```yaml
lookback_days: 1
max_executive_items: 3
batch_size: 5
```

### For Monthly Reports
```yaml
lookback_days: 30
max_executive_items: 10
batch_size: 15
```

### Cost Optimization

To minimize Claude API costs:
```yaml
processing:
  claude:
    batch_size: 15          # Larger batches
    max_tokens: 200         # Shorter summaries
```

Or disable Claude entirely (uses extractive summaries):
```python
# In src/main.py, comment out Claude initialization
# self.summarizer = Summarizer(...)
```

### Performance Optimization

For faster execution:
```yaml
collection:
  newsapi:
    enabled: true
  web_scraping:
    enabled: false        # Disable slower web scraping
  app_stores:
    enabled: false        # Disable app store collection
```

## Validation

After making config changes:

```bash
# Test configuration loads
python3 -c "from src.utils.config_loader import ConfigLoader; c = ConfigLoader(); print('Config OK')"

# Run manual test
python3 scripts/manual_run.py
```

## Advanced Configuration

### Custom Source Authority Scores

Edit `src/processors/prioritizer.py`:

```python
self.source_scores = {
    'bloomberg': 10,
    'your-custom-source': 9,
    # ...
}
```

### Custom Category Keywords

Edit `src/processors/categorizer.py`:

```python
self.category_keywords = {
    'Your Category': ['keyword1', 'keyword2'],
    # ...
}
```

## Troubleshooting

**Config not loading:**
- Check YAML syntax (use spaces, not tabs)
- Verify file exists at `config/config.yaml`
- Check for duplicate keys

**Changes not taking effect:**
- Restart the system (config loads at startup)
- Clear Python cache: `find . -type d -name "__pycache__" -exec rm -r {} +`

**Invalid configuration error:**
- Run validation: `python3 -c "from src.utils.config_loader import ConfigLoader; ConfigLoader()"`
- Check error message for specific issue
