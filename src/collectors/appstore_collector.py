"""iOS App Store collector for app information."""
from datetime import datetime
from typing import List
from .base_collector import BaseCollector, CollectedArticle
from ..utils.error_handler import retry_with_backoff

try:
    from app_store_scraper import AppStore
    APP_STORE_AVAILABLE = True
except ImportError:
    APP_STORE_AVAILABLE = False


class AppStoreCollector(BaseCollector):
    """Collector for iOS App Store data."""

    def __init__(self, config, logger):
        """Initialize App Store collector.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        super().__init__(config, logger)

        if not APP_STORE_AVAILABLE:
            self.logger.warning("app-store-scraper not available, iOS data will be skipped")

    @retry_with_backoff(max_retries=2)
    def collect(self, competitor: dict, lookback_days: int) -> List[CollectedArticle]:
        """Collect app information from iOS App Store.

        Args:
            competitor: Competitor configuration dict
            lookback_days: Number of days to look back (not used for app store)

        Returns:
            List of CollectedArticle objects
        """
        if not APP_STORE_AVAILABLE:
            return []

        articles = []
        app_id = competitor.get('ios_app_id')

        if not app_id:
            self.logger.debug(f"No iOS app ID configured for {competitor['name']}")
            return []

        try:
            # Note: app-store-scraper uses app name, not ID
            # This is a simplified implementation
            # In production, you'd need proper app metadata fetching

            self.logger.debug(f"Collecting iOS app data for {competitor['name']}")

            # Create a pseudo-article with app store information
            article = CollectedArticle(
                url=f"https://apps.apple.com/app/id{app_id}",
                title=f"{competitor['name']} - iOS App Update Check",
                content=f"iOS App Store listing for {competitor['name']}",
                source="Apple App Store",
                published_date=datetime.utcnow(),
                competitor=competitor['name']
            )

            articles.append(article)

        except Exception as e:
            self.logger.warning(f"Failed to collect iOS data for {competitor['name']}: {e}")

        self.log_collection_stats(competitor['name'], articles)
        return articles
