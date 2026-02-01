"""Google Play Store collector for app information."""
from datetime import datetime
from typing import List
from .base_collector import BaseCollector, CollectedArticle
from ..utils.error_handler import retry_with_backoff

try:
    from google_play_scraper import app
    PLAY_STORE_AVAILABLE = True
except ImportError:
    PLAY_STORE_AVAILABLE = False


class PlayStoreCollector(BaseCollector):
    """Collector for Google Play Store data."""

    def __init__(self, config, logger):
        """Initialize Play Store collector.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        super().__init__(config, logger)

        if not PLAY_STORE_AVAILABLE:
            self.logger.warning("google-play-scraper not available, Android data will be skipped")

    @retry_with_backoff(max_retries=2)
    def collect(self, competitor: dict, lookback_days: int) -> List[CollectedArticle]:
        """Collect app information from Google Play Store.

        Args:
            competitor: Competitor configuration dict
            lookback_days: Number of days to look back (not used for app store)

        Returns:
            List of CollectedArticle objects
        """
        if not PLAY_STORE_AVAILABLE:
            return []

        articles = []
        app_id = competitor.get('android_app_id')

        if not app_id:
            self.logger.debug(f"No Android app ID configured for {competitor['name']}")
            return []

        try:
            self.logger.debug(f"Collecting Android app data for {competitor['name']}")

            # Fetch app details
            app_details = app(app_id, lang='en', country='us')

            # Check if there's a recent update
            updated = app_details.get('updated')
            version = app_details.get('version', 'Unknown')
            rating = app_details.get('score', 0)
            installs = app_details.get('installs', 'Unknown')

            # Create article with app information
            content = f"Version: {version}\nRating: {rating}/5\nInstalls: {installs}\nLast Updated: {updated}"

            article = CollectedArticle(
                url=f"https://play.google.com/store/apps/details?id={app_id}",
                title=f"{competitor['name']} - Android App Update",
                content=content,
                source="Google Play Store",
                published_date=datetime.utcnow(),
                competitor=competitor['name']
            )

            articles.append(article)

        except Exception as e:
            self.logger.warning(f"Failed to collect Android data for {competitor['name']}: {e}")

        self.log_collection_stats(competitor['name'], articles)
        return articles
