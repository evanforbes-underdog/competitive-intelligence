"""Web scraper for industry news sites."""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List
from .base_collector import BaseCollector, CollectedArticle
from ..utils.error_handler import retry_with_backoff
from ..utils.rate_limiter import SimpleRateLimiter
import time


class WebScraper(BaseCollector):
    """Web scraper for industry news websites."""

    def __init__(self, config, logger):
        """Initialize web scraper.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        super().__init__(config, logger)
        self.rate_limiter = SimpleRateLimiter(
            config.get('rate_limits.web_scraping_delay_seconds', 2)
        )
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.current_ua_index = 0

    def collect(self, competitor: dict, lookback_days: int) -> List[CollectedArticle]:
        """Collect articles by scraping configured websites.

        Args:
            competitor: Competitor configuration dict
            lookback_days: Number of days to look back

        Returns:
            List of CollectedArticle objects
        """
        articles = []
        sources = self.config.get('collection.web_scraping.sources', [])

        for source in sources:
            try:
                source_articles = self._scrape_source(source, competitor, lookback_days)
                articles.extend(source_articles)
            except Exception as e:
                self.logger.warning(f"Failed to scrape {source.get('name', 'Unknown')}: {e}")

        self.log_collection_stats(competitor['name'], articles)
        return articles

    @retry_with_backoff(max_retries=2)
    def _scrape_source(
        self,
        source: dict,
        competitor: dict,
        lookback_days: int
    ) -> List[CollectedArticle]:
        """Scrape a single news source.

        Args:
            source: Source configuration dict
            competitor: Competitor configuration dict
            lookback_days: Number of days to look back

        Returns:
            List of CollectedArticle objects
        """
        articles = []

        # Rate limiting
        self.rate_limiter.acquire()

        # Rotate user agent
        headers = {
            'User-Agent': self.user_agents[self.current_ua_index % len(self.user_agents)]
        }
        self.current_ua_index += 1

        # Fetch page
        self.logger.debug(f"Scraping {source['name']}: {source['url']}")
        response = requests.get(source['url'], headers=headers, timeout=15)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')

        # Find articles using selector
        article_elements = soup.select(source.get('selector', 'article'))

        # Check if any competitor keywords are mentioned
        competitor_keywords = [kw.lower() for kw in competitor.get('keywords', [])]
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

        for element in article_elements[:50]:  # Limit to first 50 articles
            try:
                article = self._parse_article_element(
                    element,
                    source['name'],
                    competitor['name'],
                    competitor_keywords,
                    cutoff_date
                )
                if article:
                    articles.append(article)
            except Exception as e:
                self.logger.debug(f"Failed to parse article element: {e}")
                continue

        return articles

    def _parse_article_element(
        self,
        element,
        source_name: str,
        competitor: str,
        keywords: List[str],
        cutoff_date: datetime
    ) -> CollectedArticle:
        """Parse an article element from HTML.

        Args:
            element: BeautifulSoup element
            source_name: Name of the source
            competitor: Competitor name
            keywords: List of competitor keywords
            cutoff_date: Ignore articles older than this

        Returns:
            CollectedArticle or None if not relevant
        """
        # Extract title
        title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)

        # Extract link
        link_elem = element.find('a', href=True)
        if not link_elem:
            return None

        url = link_elem['href']
        if not url.startswith('http'):
            # Handle relative URLs - would need base URL
            return None

        # Extract excerpt/content
        content_elem = element.find(['p', 'div'], class_=['excerpt', 'summary', 'description'])
        content = content_elem.get_text(strip=True) if content_elem else title

        # Check if competitor is mentioned
        full_text = f"{title} {content}".lower()
        if not any(keyword in full_text for keyword in keywords):
            return None

        # Try to extract date (simple heuristic)
        time_elem = element.find('time')
        published_date = datetime.utcnow()

        if time_elem and time_elem.get('datetime'):
            try:
                published_date = datetime.fromisoformat(
                    time_elem['datetime'].replace('Z', '+00:00')
                )
            except:
                pass

        # Skip if too old
        if published_date < cutoff_date:
            return None

        return CollectedArticle(
            url=url,
            title=title,
            content=content,
            source=source_name,
            published_date=published_date,
            competitor=competitor
        )
