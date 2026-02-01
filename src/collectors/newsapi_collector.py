"""NewsAPI collector for gathering news articles."""
import requests
from datetime import datetime, timedelta
from typing import List
from .base_collector import BaseCollector, CollectedArticle
from ..utils.error_handler import retry_with_backoff
from ..utils.rate_limiter import get_rate_limiter


class NewsAPICollector(BaseCollector):
    """Collector for NewsAPI.org."""

    def __init__(self, config, logger, api_key: str):
        """Initialize NewsAPI collector.

        Args:
            config: Configuration object
            logger: Logger instance
            api_key: NewsAPI.org API key
        """
        super().__init__(config, logger)
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
        self.rate_limiter = get_rate_limiter("newsapi", 100, 86400)  # 100 per day

    @retry_with_backoff(max_retries=3)
    def collect(self, competitor: dict, lookback_days: int) -> List[CollectedArticle]:
        """Collect articles for a competitor from NewsAPI.

        Args:
            competitor: Competitor configuration dict
            lookback_days: Number of days to look back

        Returns:
            List of CollectedArticle objects
        """
        articles = []

        # Calculate date range
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=lookback_days)

        # Build query from keywords
        keywords = competitor.get('keywords', [])
        query = ' OR '.join(f'"{keyword}"' for keyword in keywords)

        # Add industry terms
        industry_terms = ["sports betting", "dfs", "daily fantasy", "sportsbook", "prediction market"]
        query = f"({query}) AND ({' OR '.join(industry_terms)})"

        # Rate limiting
        self.rate_limiter.acquire()

        # Make API request
        params = {
            'q': query,
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'language': self.config.get('collection.newsapi.search_language', 'en'),
            'sortBy': self.config.get('collection.newsapi.sort_by', 'publishedAt'),
            'apiKey': self.api_key,
            'pageSize': 100
        }

        try:
            self.logger.debug(f"Querying NewsAPI for {competitor['name']}: {query}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'ok':
                self.logger.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return articles

            # Process articles
            for article_data in data.get('articles', []):
                try:
                    article = self._parse_article(article_data, competitor['name'])
                    if article:
                        articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Failed to parse article: {e}")
                    continue

            self.log_collection_stats(competitor['name'], articles)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"NewsAPI request failed for {competitor['name']}: {e}")
            raise

        return articles

    def _parse_article(self, data: dict, competitor: str) -> CollectedArticle:
        """Parse NewsAPI article data.

        Args:
            data: Article data from NewsAPI
            competitor: Competitor name

        Returns:
            CollectedArticle object or None if invalid
        """
        # Skip articles with removed content
        if data.get('title') == '[Removed]' or not data.get('url'):
            return None

        # Parse published date
        published_str = data.get('publishedAt', '')
        try:
            published_date = datetime.strptime(published_str, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            published_date = datetime.utcnow()

        # Combine description and content
        content = data.get('content', '') or ''
        description = data.get('description', '') or ''
        full_content = f"{description}\n\n{content}".strip()

        return CollectedArticle(
            url=data['url'],
            title=data.get('title', 'No Title'),
            content=full_content,
            source=data.get('source', {}).get('name', 'Unknown'),
            published_date=published_date,
            competitor=competitor
        )
