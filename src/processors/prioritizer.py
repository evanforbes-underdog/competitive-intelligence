"""Article prioritization for executive summary."""
from datetime import datetime
from typing import Dict, List


class Prioritizer:
    """Calculate priority scores for articles."""

    def __init__(self, config, logger):
        """Initialize prioritizer.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger

        # Load weights from config
        weights = config.get('processing.priority_weights', {})
        self.recency_weight = weights.get('recency', 0.3)
        self.source_weight = weights.get('source_authority', 0.25)
        self.category_weight = weights.get('category_importance', 0.25)
        self.competitor_weight = weights.get('competitor_priority', 0.2)

        # Source authority scores (0-10)
        self.source_scores = {
            'bloomberg': 10,
            'reuters': 10,
            'wall street journal': 10,
            'financial times': 9,
            'techcrunch': 9,
            'the athletic': 8,
            'espn': 8,
            'sports business journal': 9,
            'sbc news': 8,
            'sports handle': 7,
            'legal sports report': 8,
            'google play store': 6,
            'apple app store': 6,
        }

        # Category importance scores (0-10)
        self.category_scores = {
            'Regulatory News': 10,  # HIGHEST PRIORITY
            'Funding': 10,
            'Executive Moves': 9,
            'Product Updates': 8,
            'Partnerships': 7,
            'Marketing Campaigns': 6,
            'Promotions': 4,
            'Other': 5
        }

        # Competitor priority from config
        self.competitor_priorities = {}
        for competitor in config.get('competitors', []):
            priority = competitor.get('priority', 'medium')
            score = {'high': 10, 'medium': 7, 'low': 5}.get(priority, 7)
            self.competitor_priorities[competitor['name']] = score

    def calculate_priority(
        self,
        published_date: datetime,
        source: str,
        category: str,
        competitor: str
    ) -> float:
        """Calculate priority score for an article.

        Args:
            published_date: When the article was published
            source: Article source name
            category: Article category
            competitor: Competitor name

        Returns:
            Priority score (0-10)
        """
        # Recency score (0-10, based on days old)
        days_old = (datetime.utcnow() - published_date).days
        recency_score = max(10 - days_old, 1)  # Newer = higher score

        # Source authority score
        source_lower = source.lower()
        source_score = 5  # Default
        for key, score in self.source_scores.items():
            if key in source_lower:
                source_score = score
                break

        # Category importance score
        category_score = self.category_scores.get(category, 5)

        # Competitor priority score
        competitor_score = self.competitor_priorities.get(competitor, 7)

        # Weighted average
        priority = (
            recency_score * self.recency_weight +
            source_score * self.source_weight +
            category_score * self.category_weight +
            competitor_score * self.competitor_weight
        )

        return round(priority, 2)

    def prioritize_batch(self, articles: List[Dict]) -> List[Dict]:
        """Calculate priorities for a batch of articles.

        Args:
            articles: List of article dicts with metadata

        Returns:
            List of dicts with 'url' and 'priority_score'
        """
        results = []

        for article in articles:
            priority = self.calculate_priority(
                article.get('published_date', datetime.utcnow()),
                article.get('source', ''),
                article.get('category', 'Other'),
                article.get('competitor', '')
            )

            results.append({
                'url': article['url'],
                'priority_score': priority
            })

        return results

    def get_top_articles(
        self,
        articles: List[tuple],
        limit: int = 5
    ) -> List[tuple]:
        """Get top N articles by priority.

        Args:
            articles: List of (Article, Summary) tuples
            limit: Number of top articles to return

        Returns:
            List of top articles sorted by priority
        """
        # Sort by priority score (highest first)
        sorted_articles = sorted(
            articles,
            key=lambda x: x[1].priority_score if len(x) > 1 else 0,
            reverse=True
        )

        return sorted_articles[:limit]
