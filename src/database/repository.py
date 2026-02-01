"""Data access layer for database operations."""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from .models import Article, Summary, Report, ExecutionLog, get_engine
import hashlib


class Repository:
    """Repository pattern for database operations."""

    def __init__(self, database_path: str):
        """Initialize repository with database connection.

        Args:
            database_path: Path to SQLite database file
        """
        self.engine = get_engine(database_path)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    # Article operations

    def article_exists(self, url: str = None, content_hash: str = None) -> bool:
        """Check if an article already exists.

        Args:
            url: Article URL
            content_hash: Content hash

        Returns:
            True if article exists
        """
        with self.get_session() as session:
            query = session.query(Article)

            if url:
                query = query.filter(Article.url == url)
            elif content_hash:
                query = query.filter(Article.content_hash == content_hash)
            else:
                return False

            return query.first() is not None

    def add_article(self, article: Article) -> Optional[Article]:
        """Add a new article to the database.

        Args:
            article: Article object to add

        Returns:
            Added article or None if duplicate
        """
        with self.get_session() as session:
            try:
                # Generate hash if not present
                if not article.content_hash:
                    article.content_hash = article.generate_content_hash()

                session.add(article)
                session.commit()
                session.refresh(article)
                return article
            except IntegrityError:
                session.rollback()
                return None

    def get_articles_without_summary(self, limit: int = None) -> List[Article]:
        """Get articles that don't have summaries yet.

        Args:
            limit: Maximum number of articles to return

        Returns:
            List of articles without summaries
        """
        with self.get_session() as session:
            query = session.query(Article).outerjoin(Summary).filter(Summary.id == None)

            if limit:
                query = query.limit(limit)

            return query.all()

    def get_articles_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        competitor: str = None
    ) -> List[Article]:
        """Get articles within a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            competitor: Optional competitor filter

        Returns:
            List of articles
        """
        with self.get_session() as session:
            query = session.query(Article).filter(
                Article.published_date >= start_date,
                Article.published_date <= end_date
            )

            if competitor:
                query = query.filter(Article.competitor == competitor)

            return query.order_by(Article.published_date.desc()).all()

    # Summary operations

    def add_summary(self, summary: Summary) -> Summary:
        """Add a summary to the database.

        Args:
            summary: Summary object to add

        Returns:
            Added summary
        """
        with self.get_session() as session:
            session.add(summary)
            session.commit()
            session.refresh(summary)
            return summary

    def get_summary_by_article_id(self, article_id: int) -> Optional[Summary]:
        """Get summary for an article.

        Args:
            article_id: Article ID

        Returns:
            Summary or None
        """
        with self.get_session() as session:
            return session.query(Summary).filter(Summary.article_id == article_id).first()

    # Report operations

    def add_report(self, report: Report) -> Report:
        """Add a report to the database.

        Args:
            report: Report object to add

        Returns:
            Added report
        """
        with self.get_session() as session:
            session.add(report)
            session.commit()
            session.refresh(report)
            return report

    def update_report_status(self, report_id: int, status: str, error_message: str = None):
        """Update report status.

        Args:
            report_id: Report ID
            status: New status
            error_message: Optional error message
        """
        with self.get_session() as session:
            report = session.query(Report).filter(Report.id == report_id).first()
            if report:
                report.status = status
                if error_message:
                    report.error_message = error_message
                if status == 'sent':
                    report.sent_date = datetime.utcnow()
                session.commit()

    def get_latest_report(self) -> Optional[Report]:
        """Get the most recent report.

        Returns:
            Latest report or None
        """
        with self.get_session() as session:
            return session.query(Report).order_by(Report.report_date.desc()).first()

    # Execution log operations

    def add_execution_log(self, log: ExecutionLog) -> ExecutionLog:
        """Add an execution log entry.

        Args:
            log: ExecutionLog object to add

        Returns:
            Added log entry
        """
        with self.get_session() as session:
            session.add(log)
            session.commit()
            session.refresh(log)
            return log

    def get_recent_execution_logs(self, limit: int = 10) -> List[ExecutionLog]:
        """Get recent execution logs.

        Args:
            limit: Maximum number of logs to return

        Returns:
            List of execution logs
        """
        with self.get_session() as session:
            return session.query(ExecutionLog).order_by(
                ExecutionLog.run_date.desc()
            ).limit(limit).all()

    # Reporting queries

    def get_articles_with_summaries_by_date(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[tuple]:
        """Get articles with their summaries for a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of (Article, Summary) tuples
        """
        with self.get_session() as session:
            results = session.query(Article, Summary).join(
                Summary, Article.id == Summary.article_id
            ).filter(
                Article.published_date >= start_date,
                Article.published_date <= end_date
            ).order_by(
                Summary.priority_score.desc(),
                Article.published_date.desc()
            ).all()

            return results

    def get_competitor_article_counts(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Get article counts by competitor for a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Dictionary mapping competitor names to article counts
        """
        with self.get_session() as session:
            results = session.query(
                Article.competitor,
                Article.id
            ).filter(
                Article.published_date >= start_date,
                Article.published_date <= end_date
            ).all()

            counts = {}
            for competitor, _ in results:
                counts[competitor] = counts.get(competitor, 0) + 1

            return counts

    # Maintenance operations

    def cleanup_old_data(self, days: int = 90):
        """Remove old articles and summaries.

        Args:
            days: Remove data older than this many days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        with self.get_session() as session:
            session.query(Article).filter(
                Article.collected_date < cutoff_date
            ).delete()
            session.commit()
