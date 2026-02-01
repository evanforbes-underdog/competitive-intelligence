"""Article categorization using hybrid keyword + AI approach."""
from typing import Dict
from ..utils.error_handler import GracefulDegradation


class Categorizer:
    """Hybrid categorizer for article classification."""

    def __init__(self, config, logger):
        """Initialize categorizer.

        Args:
            config: Configuration object
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.categories = config.get('processing.categories', [
            'Product Updates',
            'Marketing Campaigns',
            'Partnerships',
            'Regulatory News',
            'Promotions',
            'Executive Moves',
            'Funding',
            'Other'
        ])

        # Keyword patterns for each category
        self.category_keywords = {
            'Product Updates': [
                'launch', 'feature', 'update', 'new app', 'release', 'version',
                'beta', 'rolled out', 'introduced', 'redesign', 'upgrade'
            ],
            'Marketing Campaigns': [
                'campaign', 'advertising', 'marketing', 'brand', 'commercial',
                'ambassador', 'spokesperson', 'super bowl', 'ad campaign'
            ],
            'Partnerships': [
                'partner', 'partnership', 'deal', 'agreement', 'collaborate',
                'team up', 'alliance', 'joint venture', 'sponsor', 'sponsorship'
            ],
            'Regulatory News': [
                'regulation', 'legal', 'law', 'compliance', 'license', 'regulator',
                'court', 'lawsuit', 'fine', 'penalty', 'settlement', 'approved',
                'gambling commission', 'gaming board'
            ],
            'Promotions': [
                'bonus', 'offer', 'promo', 'deposit', 'free bet', 'odds boost',
                'promotion', 'deal', 'special offer', 'limited time', 'risk free'
            ],
            'Executive Moves': [
                'ceo', 'executive', 'hire', 'appoint', 'resign', 'joins',
                'promoted', 'chief', 'officer', 'director', 'board', 'founder'
            ],
            'Funding': [
                'funding', 'investment', 'raise', 'series', 'valuation', 'ipo',
                'round', 'venture capital', 'investors', 'acquired', 'acquisition',
                'merger', 'revenue', 'earnings'
            ]
        }

    def categorize(self, title: str, content: str, summary: str = "") -> Dict[str, any]:
        """Categorize an article using keyword matching.

        Args:
            title: Article title
            content: Article content
            summary: Optional article summary

        Returns:
            Dict with 'category' and 'confidence' keys
        """
        text = f"{title} {summary} {content}".lower()

        # Score each category
        category_scores = {}

        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score

        # Return category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            max_score = category_scores[best_category]

            # Calculate confidence (normalize to 0-1)
            confidence = min(max_score / 3.0, 1.0)

            return {
                'category': best_category,
                'confidence': confidence
            }

        # Default to 'Other' if no keywords matched
        return {
            'category': 'Other',
            'confidence': 0.5
        }

    def categorize_batch(self, articles: list) -> list:
        """Categorize a batch of articles.

        Args:
            articles: List of article dicts with 'title', 'content', 'summary'

        Returns:
            List of category dicts
        """
        results = []

        for article in articles:
            result = self.categorize(
                article.get('title', ''),
                article.get('content', ''),
                article.get('summary', '')
            )
            result['url'] = article.get('url', '')
            results.append(result)

        return results
