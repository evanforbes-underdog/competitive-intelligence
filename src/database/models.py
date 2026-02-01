"""Database models for competitive intelligence system."""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import hashlib

Base = declarative_base()


class Article(Base):
    """Article model for storing collected news articles."""

    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    url = Column(String(500), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    source = Column(String(100), nullable=False)
    published_date = Column(DateTime, nullable=False, index=True)
    competitor = Column(String(100), nullable=False, index=True)
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    collected_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    summary = relationship("Summary", back_populates="article", uselist=False, cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        """Initialize article and generate content hash."""
        super().__init__(**kwargs)
        if 'content_hash' not in kwargs and self.content:
            self.content_hash = self.generate_content_hash()

    def generate_content_hash(self) -> str:
        """Generate SHA-256 hash of title + content for deduplication."""
        content_str = f"{self.title}:{self.content or ''}"
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', competitor='{self.competitor}')>"


class Summary(Base):
    """Summary model for storing AI-generated summaries."""

    __tablename__ = 'summaries'

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'), unique=True, nullable=False, index=True)
    summary_text = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    priority_score = Column(Float, default=5.0)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    article = relationship("Article", back_populates="summary")

    def __repr__(self):
        return f"<Summary(id={self.id}, category='{self.category}', priority={self.priority_score})>"


class Report(Base):
    """Report model for tracking generated reports."""

    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    report_date = Column(DateTime, nullable=False, index=True)
    total_articles = Column(Integer, default=0)
    sent_date = Column(DateTime)
    status = Column(String(20), default='pending')  # pending, sent, failed
    error_message = Column(Text)
    recipients = Column(String(500))

    def __repr__(self):
        return f"<Report(id={self.id}, date={self.report_date}, status='{self.status}')>"


class ExecutionLog(Base):
    """Execution log model for tracking system runs."""

    __tablename__ = 'execution_logs'

    id = Column(Integer, primary_key=True)
    run_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(String(20), nullable=False)  # success, partial, failed
    duration_seconds = Column(Float)
    articles_collected = Column(Integer, default=0)
    articles_new = Column(Integer, default=0)
    summaries_generated = Column(Integer, default=0)
    error_message = Column(Text)
    details = Column(Text)  # JSON string with detailed metrics

    def __repr__(self):
        return f"<ExecutionLog(id={self.id}, date={self.run_date}, status='{self.status}')>"


def create_tables(engine):
    """Create all tables in the database.

    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(engine)


def get_engine(database_path: str):
    """Create and return a database engine.

    Args:
        database_path: Path to SQLite database file

    Returns:
        SQLAlchemy engine
    """
    return create_engine(f'sqlite:///{database_path}', echo=False)
