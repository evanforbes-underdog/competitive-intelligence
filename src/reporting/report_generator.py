"""Report generation for competitive intelligence."""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from collections import defaultdict


class ReportGenerator:
    """Generate HTML reports from collected data."""

    def __init__(self, config, logger, repository):
        """Initialize report generator.

        Args:
            config: Configuration object
            logger: Logger instance
            repository: Database repository
        """
        self.config = config
        self.logger = logger
        self.repository = repository

        # Set up Jinja2 template environment
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))

    def generate_report(self, start_date: datetime, end_date: datetime) -> str:
        """Generate HTML report for date range.

        Args:
            start_date: Start of reporting period
            end_date: End of reporting period

        Returns:
            HTML report string
        """
        self.logger.info(f"Generating report for {start_date.date()} to {end_date.date()}")

        # Fetch articles with summaries
        articles_with_summaries = self.repository.get_articles_with_summaries_by_date(
            start_date, end_date
        )

        if not articles_with_summaries:
            self.logger.warning("No articles found for report period")
            return self._generate_empty_report(start_date, end_date)

        # Group articles by competitor
        competitors_data = self._group_by_competitor(articles_with_summaries)

        # Get top items for executive summary
        max_exec_items = self.config.get('reporting.email.max_executive_items', 5)
        executive_items = self._get_executive_items(articles_with_summaries, max_exec_items)

        # Collect sources
        sources = self._collect_sources(articles_with_summaries)

        # Prepare template data
        template_data = {
            'report_date': datetime.utcnow().strftime('%B %d, %Y'),
            'date_range': f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}",
            'total_articles': len(articles_with_summaries),
            'num_competitors': len(competitors_data),
            'executive_items': executive_items,
            'competitors': competitors_data,
            'sources': ', '.join(sources),
            'generation_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        }

        # Render template
        template = self.jinja_env.get_template('email_template.html')
        html_report = template.render(**template_data)

        self.logger.info(f"Report generated with {len(articles_with_summaries)} articles")
        return html_report

    def _group_by_competitor(self, articles: List[Tuple]) -> Dict[str, List[Dict]]:
        """Group articles by competitor.

        Args:
            articles: List of (Article, Summary) tuples

        Returns:
            Dict mapping competitor names to article data
        """
        grouped = defaultdict(list)

        for article, summary in articles:
            article_data = {
                'title': article.title,
                'url': article.url,
                'source': article.source,
                'published_date': article.published_date.strftime('%b %d, %Y'),
                'summary': summary.summary_text,
                'category': summary.category,
                'category_class': self._get_category_class(summary.category),
                'priority_score': summary.priority_score
            }

            grouped[article.competitor].append(article_data)

        # Sort articles within each competitor by priority
        for competitor in grouped:
            grouped[competitor] = sorted(
                grouped[competitor],
                key=lambda x: x['priority_score'],
                reverse=True
            )

        return dict(grouped)

    def _get_executive_items(self, articles: List[Tuple], limit: int) -> List[Dict]:
        """Get top priority items for executive summary.

        Args:
            articles: List of (Article, Summary) tuples
            limit: Maximum number of items

        Returns:
            List of top article data
        """
        # Sort by priority score
        sorted_articles = sorted(
            articles,
            key=lambda x: x[1].priority_score,
            reverse=True
        )

        executive_items = []

        for article, summary in sorted_articles[:limit]:
            item = {
                'title': article.title,
                'url': article.url,
                'competitor': article.competitor,
                'source': article.source,
                'published_date': article.published_date.strftime('%b %d, %Y'),
                'summary': summary.summary_text,
                'category': summary.category,
                'category_class': self._get_category_class(summary.category),
                'priority_score': summary.priority_score
            }
            executive_items.append(item)

        return executive_items

    def _collect_sources(self, articles: List[Tuple]) -> List[str]:
        """Collect unique sources from articles.

        Args:
            articles: List of (Article, Summary) tuples

        Returns:
            List of unique source names
        """
        sources = set()
        for article, _ in articles:
            sources.add(article.source)

        return sorted(list(sources))

    def _get_category_class(self, category: str) -> str:
        """Get CSS class for category.

        Args:
            category: Category name

        Returns:
            CSS class name
        """
        category_map = {
            'Product Updates': 'product',
            'Marketing Campaigns': 'marketing',
            'Partnerships': 'partnerships',
            'Regulatory News': 'regulatory',
            'Promotions': 'promotions',
            'Executive Moves': 'executive',
            'Funding': 'funding',
            'Other': 'other'
        }

        return category_map.get(category, 'other')

    def _generate_empty_report(self, start_date: datetime, end_date: datetime) -> str:
        """Generate report when no articles are found.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            HTML report string
        """
        template_data = {
            'report_date': datetime.utcnow().strftime('%B %d, %Y'),
            'date_range': f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}",
            'total_articles': 0,
            'num_competitors': 0,
            'executive_items': [],
            'competitors': {},
            'sources': 'None',
            'generation_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        }

        template = self.jinja_env.get_template('email_template.html')
        return template.render(**template_data)
