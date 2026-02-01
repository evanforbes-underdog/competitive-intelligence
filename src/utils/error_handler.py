"""Error handling utilities with retry logic and circuit breaker."""
import time
import functools
from typing import Callable, Type, Tuple
from enum import Enum


class ErrorType(Enum):
    """Classification of error types."""
    TRANSIENT = "transient"  # Retry
    PERMANENT = "permanent"  # Skip
    CRITICAL = "critical"    # Abort


def classify_error(error: Exception) -> ErrorType:
    """Classify an error to determine handling strategy.

    Args:
        error: The exception to classify

    Returns:
        ErrorType classification
    """
    error_str = str(error).lower()
    error_type = type(error).__name__

    # Critical errors
    if "authentication" in error_str or "api key" in error_str:
        return ErrorType.CRITICAL

    # Transient errors
    transient_indicators = [
        "timeout", "connection", "network", "503", "502", "500",
        "rate limit", "too many requests", "429"
    ]
    if any(indicator in error_str for indicator in transient_indicators):
        return ErrorType.TRANSIENT

    # Permanent errors
    permanent_indicators = ["404", "400", "401", "403", "invalid", "not found"]
    if any(indicator in error_str for indicator in permanent_indicators):
        return ErrorType.PERMANENT

    # Default to transient for unknown errors
    return ErrorType.TRANSIENT


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = base_delay

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    error_type = classify_error(e)

                    if error_type == ErrorType.CRITICAL:
                        raise

                    if error_type == ErrorType.PERMANENT:
                        raise

                    # Transient error - retry
                    retries += 1
                    if retries > max_retries:
                        raise

                    time.sleep(delay)
                    delay *= backoff_factor

            return None

        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func: Callable, *args, **kwargs):
        """Call a function through the circuit breaker.

        Args:
            func: Function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "open":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        self.failures = 0
        self.state = "closed"

    def _on_failure(self):
        """Handle failed call."""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = "open"


class GracefulDegradation:
    """Strategies for graceful degradation when services fail."""

    @staticmethod
    def extractive_summary(text: str, sentences: int = 3) -> str:
        """Create a simple extractive summary by taking first N sentences.

        Args:
            text: Text to summarize
            sentences: Number of sentences to extract

        Returns:
            Extractive summary
        """
        if not text:
            return ""

        # Simple sentence splitting
        import re
        sentence_endings = re.compile(r'[.!?]\s+')
        sentences_list = sentence_endings.split(text)

        # Take first N sentences
        summary_sentences = sentences_list[:sentences]
        summary = '. '.join(s.strip() for s in summary_sentences if s.strip())

        if summary and not summary.endswith('.'):
            summary += '.'

        return summary

    @staticmethod
    def keyword_categorize(text: str, title: str = "") -> str:
        """Simple keyword-based categorization fallback.

        Args:
            text: Article text
            title: Article title

        Returns:
            Category name
        """
        content = (title + " " + text).lower()

        category_keywords = {
            "Product Updates": ["launch", "feature", "update", "new app", "release", "version"],
            "Marketing Campaigns": ["campaign", "advertising", "marketing", "promotion", "brand"],
            "Partnerships": ["partner", "partnership", "deal", "agreement", "collaborate"],
            "Regulatory News": ["regulation", "legal", "law", "compliance", "license", "regulator"],
            "Promotions": ["bonus", "offer", "promo", "deposit", "free bet", "odds boost"],
            "Executive Moves": ["ceo", "executive", "hire", "appoint", "resign", "joins"],
            "Funding": ["funding", "investment", "raise", "series", "valuation", "ipo"]
        }

        for category, keywords in category_keywords.items():
            if any(keyword in content for keyword in keywords):
                return category

        return "Other"
