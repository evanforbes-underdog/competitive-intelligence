#!/usr/bin/env python3
"""Main orchestrator for competitive intelligence system."""
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config_loader import ConfigLoader
from src.utils.logger import Logger
from src.utils.error_handler import ErrorType, classify_error
from src.database.repository import Repository
from src.database.models import Article, Summary, Report, ExecutionLog, create_tables, get_engine
from src.collectors.newsapi_collector import NewsAPICollector
from src.collectors.web_scraper import WebScraper
from src.collectors.appstore_collector import AppStoreCollector
from src.collectors.playstore_collector import PlayStoreCollector
from src.processors.summarizer import Summarizer
from src.processors.categorizer import Categorizer
from src.processors.prioritizer import Prioritizer
from src.reporting.report_generator import ReportGenerator
from src.reporting.email_sender import EmailSender


class CompetitiveIntelligenceSystem:
    """Main system orchestrator."""

    def __init__(self):
        """Initialize the system."""
        # Load configuration
        self.config = ConfigLoader()

        # Set up logging
        log_path = self.config.get_log_path()
        self.logger = Logger.get_logger(__name__, log_path, self.config.get('logging.level', 'INFO'))

        self.logger.info("=" * 80)
        self.logger.info("Competitive Intelligence System Starting")
        self.logger.info("=" * 80)

        # Initialize database
        db_path = self.config.get_database_path()
        self.logger.info(f"Database: {db_path}")

        # Create tables if needed
        engine = get_engine(str(db_path))
        create_tables(engine)

        self.repository = Repository(str(db_path))

        # Initialize collectors
        self.collectors = []

        if self.config.get('collection.newsapi.enabled', True):
            newsapi_key = self.config.get_env('NEWSAPI_KEY')
            if newsapi_key:
                self.collectors.append(
                    NewsAPICollector(self.config, self.logger, newsapi_key)
                )
                self.logger.info("NewsAPI collector enabled")

        if self.config.get('collection.web_scraping.enabled', True):
            self.collectors.append(WebScraper(self.config, self.logger))
            self.logger.info("Web scraper enabled")

        if self.config.get('collection.app_stores.enabled', False):
            self.collectors.append(AppStoreCollector(self.config, self.logger))
            self.collectors.append(PlayStoreCollector(self.config, self.logger))
            self.logger.info("App store collectors enabled")

        # Initialize processors
        anthropic_key = self.config.get_env('ANTHROPIC_API_KEY')
        self.summarizer = Summarizer(self.config, self.logger, anthropic_key)
        self.categorizer = Categorizer(self.config, self.logger)
        self.prioritizer = Prioritizer(self.config, self.logger)

        # Initialize reporting
        self.report_generator = ReportGenerator(self.config, self.logger, self.repository)

        gmail_user = self.config.get_env('GMAIL_USERNAME')
        gmail_pass = self.config.get_env('GMAIL_APP_PASSWORD')
        self.email_sender = EmailSender(self.config, self.logger, gmail_user, gmail_pass)

        # Execution metrics
        self.metrics = {
            'articles_collected': 0,
            'articles_new': 0,
            'articles_duplicate': 0,
            'summaries_generated': 0,
            'errors': []
        }

    def run(self):
        """Execute the full pipeline."""
        start_time = time.time()
        status = 'success'

        try:
            # Step 1: Data Collection
            self.logger.info("Step 1: Collecting articles")
            articles = self._collect_articles()

            # Step 2: Deduplication and Storage
            self.logger.info("Step 2: Deduplicating and storing articles")
            new_articles = self._store_articles(articles)

            # Step 3: Processing
            self.logger.info("Step 3: Processing articles (summarize, categorize, prioritize)")
            self._process_articles(new_articles)

            # Step 4: Generate Report
            self.logger.info("Step 4: Generating report")
            report, html_content = self._generate_report()

            # Step 5: Send Email
            self.logger.info("Step 5: Sending email")
            self._send_email(report, html_content)

            self.logger.info("Pipeline completed successfully")

        except Exception as e:
            status = 'failed'
            error_type = classify_error(e)
            self.logger.error(f"Pipeline failed ({error_type.value}): {e}", exc_info=True)
            self.metrics['errors'].append(str(e))

            if error_type == ErrorType.CRITICAL:
                raise

        finally:
            # Log execution
            duration = time.time() - start_time
            self._log_execution(status, duration)

            self.logger.info(f"Execution completed in {duration:.2f} seconds")
            self.logger.info(f"Metrics: {json.dumps(self.metrics, indent=2)}")

    def _collect_articles(self) -> list:
        """Collect articles from all sources.

        Returns:
            List of CollectedArticle objects
        """
        all_articles = []
        competitors = self.config.get_competitors()
        lookback_days = self.config.get('collection.lookback_days', 7)

        for competitor in competitors:
            self.logger.info(f"Collecting articles for {competitor['name']}")

            for collector in self.collectors:
                try:
                    articles = collector.collect(competitor, lookback_days)
                    all_articles.extend(articles)
                    self.metrics['articles_collected'] += len(articles)

                except Exception as e:
                    error_type = classify_error(e)
                    self.logger.warning(
                        f"Collector {collector.__class__.__name__} failed for "
                        f"{competitor['name']}: {e} ({error_type.value})"
                    )
                    self.metrics['errors'].append(
                        f"{collector.__class__.__name__}: {str(e)}"
                    )

                    if error_type == ErrorType.CRITICAL:
                        raise

        self.logger.info(f"Collected {len(all_articles)} total articles")
        return all_articles

    def _store_articles(self, articles: list) -> list:
        """Store articles in database, filtering duplicates.

        Args:
            articles: List of CollectedArticle objects

        Returns:
            List of newly stored Article objects
        """
        new_articles = []

        for collected_article in articles:
            # Check if already exists
            if self.repository.article_exists(url=collected_article.url):
                self.metrics['articles_duplicate'] += 1
                continue

            # Create Article model
            article = Article(
                url=collected_article.url,
                title=collected_article.title,
                content=collected_article.content,
                source=collected_article.source,
                published_date=collected_article.published_date,
                competitor=collected_article.competitor
            )

            # Store in database
            stored_article = self.repository.add_article(article)

            if stored_article:
                new_articles.append(stored_article)
                self.metrics['articles_new'] += 1
            else:
                self.metrics['articles_duplicate'] += 1

        self.logger.info(
            f"Stored {len(new_articles)} new articles "
            f"({self.metrics['articles_duplicate']} duplicates skipped)"
        )

        return new_articles

    def _process_articles(self, articles: list):
        """Process articles: summarize, categorize, prioritize.

        Args:
            articles: List of Article objects
        """
        if not articles:
            self.logger.info("No new articles to process")
            return

        # Prepare article data for batch processing
        article_data = [
            {
                'url': article.url,
                'title': article.title,
                'content': article.content,
                'source': article.source,
                'published_date': article.published_date,
                'competitor': article.competitor
            }
            for article in articles
        ]

        # Summarize
        self.logger.info(f"Summarizing {len(articles)} articles")
        try:
            summaries = self.summarizer.summarize_batch(article_data)
            summary_map = {s['url']: s['summary'] for s in summaries}
        except Exception as e:
            self.logger.error(f"Summarization failed: {e}")
            self.metrics['errors'].append(f"Summarization: {str(e)}")
            # Use extractive fallback
            from utils.error_handler import GracefulDegradation
            summary_map = {
                a['url']: GracefulDegradation.extractive_summary(a['content'], 3)
                for a in article_data
            }

        # Add summaries to article data
        for item in article_data:
            item['summary'] = summary_map.get(item['url'], '')

        # Categorize
        self.logger.info(f"Categorizing {len(articles)} articles")
        try:
            categories = self.categorizer.categorize_batch(article_data)
            category_map = {c['url']: c for c in categories}
        except Exception as e:
            self.logger.error(f"Categorization failed: {e}")
            self.metrics['errors'].append(f"Categorization: {str(e)}")
            category_map = {a['url']: {'category': 'Other', 'confidence': 0.5} for a in article_data}

        # Add categories to article data
        for item in article_data:
            cat_data = category_map.get(item['url'], {})
            item['category'] = cat_data.get('category', 'Other')

        # Prioritize
        self.logger.info(f"Prioritizing {len(articles)} articles")
        try:
            priorities = self.prioritizer.prioritize_batch(article_data)
            priority_map = {p['url']: p['priority_score'] for p in priorities}
        except Exception as e:
            self.logger.error(f"Prioritization failed: {e}")
            self.metrics['errors'].append(f"Prioritization: {str(e)}")
            priority_map = {a['url']: 5.0 for a in article_data}

        # Store summaries in database
        for article in articles:
            summary_text = summary_map.get(article.url, '')
            category = category_map.get(article.url, {}).get('category', 'Other')
            priority = priority_map.get(article.url, 5.0)

            summary = Summary(
                article_id=article.id,
                summary_text=summary_text,
                category=category,
                priority_score=priority
            )

            self.repository.add_summary(summary)
            self.metrics['summaries_generated'] += 1

        self.logger.info(f"Processed {len(articles)} articles")

    def _generate_report(self) -> tuple:
        """Generate HTML report.

        Returns:
            Tuple of (Report object, HTML content)
        """
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=self.config.get('collection.lookback_days', 7))

        # Generate HTML
        html_content = self.report_generator.generate_report(start_date, end_date)

        # Create report record
        recipients = self.config.get('reporting.email.recipients', [])
        report = Report(
            report_date=datetime.utcnow(),
            total_articles=self.metrics['articles_new'],
            status='pending',
            recipients=','.join(recipients)
        )

        report = self.repository.add_report(report)

        return report, html_content

    def _send_email(self, report: Report, html_content: str):
        """Send email report.

        Args:
            report: Report object
            html_content: HTML content to send
        """
        recipients = self.config.get('reporting.email.recipients', [])
        subject_template = self.config.get(
            'reporting.email.subject',
            'Weekly Competitive Intelligence Report - {date}'
        )
        subject = subject_template.format(date=datetime.utcnow().strftime('%B %d, %Y'))

        try:
            success = self.email_sender.send_report(html_content, subject, recipients)

            if success:
                self.repository.update_report_status(report.id, 'sent')
                self.logger.info("Email sent successfully")
            else:
                self.repository.update_report_status(report.id, 'failed', 'Unknown error')
                self.logger.error("Email sending failed")

        except Exception as e:
            self.repository.update_report_status(report.id, 'failed', str(e))
            self.logger.error(f"Email sending failed: {e}")
            self.metrics['errors'].append(f"Email: {str(e)}")

            # Save report to file as backup
            backup_path = Path(__file__).parent.parent / 'data' / 'reports'
            backup_path.mkdir(exist_ok=True)
            report_file = backup_path / f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"

            with open(report_file, 'w') as f:
                f.write(html_content)

            self.logger.info(f"Report saved to file: {report_file}")

    def _log_execution(self, status: str, duration: float):
        """Log execution details to database.

        Args:
            status: Execution status
            duration: Execution duration in seconds
        """
        log = ExecutionLog(
            status=status,
            duration_seconds=duration,
            articles_collected=self.metrics['articles_collected'],
            articles_new=self.metrics['articles_new'],
            summaries_generated=self.metrics['summaries_generated'],
            error_message='; '.join(self.metrics['errors']) if self.metrics['errors'] else None,
            details=json.dumps(self.metrics)
        )

        self.repository.add_execution_log(log)


def main():
    """Main entry point."""
    try:
        system = CompetitiveIntelligenceSystem()
        system.run()
        sys.exit(0)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
