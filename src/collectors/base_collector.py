"""Base collector class with common functionality."""
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class CollectedArticle:
    """Standardized article data structure."""
    url: str
    title: str
    content: str
    source: str
    published_date: datetime
    competitor: str


class BaseCollector(ABC):
    """Abstract base class for all collectors."""

    def __init__(self, config, logger):
        """Initialize collector.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger

    @abstractmethod
    def collect(self, competitor: dict, lookback_days: int) -> List[CollectedArticle]:
        """Collect articles for a competitor.

        Args:
            competitor: Competitor configuration dict
            lookback_days: Number of days to look back

        Returns:
            List of CollectedArticle objects
        """
        pass

    def log_collection_stats(self, competitor_name: str, articles: List[CollectedArticle]):
        """Log collection statistics.

        Args:
            competitor_name: Name of the competitor
            articles: List of collected articles
        """
        self.logger.info(
            f"Collected {len(articles)} articles for {competitor_name} from {self.__class__.__name__}"
        )
