"""Rate limiting utilities using token bucket algorithm."""
import time
import threading
from typing import Dict


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, requests_per_period: int, period_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            requests_per_period: Maximum number of requests allowed in the period
            period_seconds: Time period in seconds (default: 60 for per-minute limiting)
        """
        self.requests_per_period = requests_per_period
        self.period_seconds = period_seconds
        self.tokens = requests_per_period
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens from the bucket. Blocks until tokens are available.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens were acquired
        """
        with self.lock:
            self._refill()

            while self.tokens < tokens:
                time.sleep(0.1)
                self._refill()

            self.tokens -= tokens
            return True

    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill

        # Calculate tokens to add based on elapsed time
        tokens_to_add = (elapsed / self.period_seconds) * self.requests_per_period

        if tokens_to_add > 0:
            self.tokens = min(self.requests_per_period, self.tokens + tokens_to_add)
            self.last_refill = now


class SimpleRateLimiter:
    """Simple rate limiter that enforces minimum delay between requests."""

    def __init__(self, delay_seconds: float):
        """Initialize rate limiter.

        Args:
            delay_seconds: Minimum delay between requests
        """
        self.delay_seconds = delay_seconds
        self.last_request = 0
        self.lock = threading.Lock()

    def acquire(self):
        """Wait until enough time has passed since the last request."""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_request

            if elapsed < self.delay_seconds:
                time.sleep(self.delay_seconds - elapsed)

            self.last_request = time.time()


# Global rate limiters
_rate_limiters: Dict[str, RateLimiter] = {}


def get_rate_limiter(name: str, requests_per_period: int, period_seconds: int = 60) -> RateLimiter:
    """Get or create a rate limiter.

    Args:
        name: Unique name for the rate limiter
        requests_per_period: Maximum requests allowed in the period
        period_seconds: Time period in seconds

    Returns:
        RateLimiter instance
    """
    if name not in _rate_limiters:
        _rate_limiters[name] = RateLimiter(requests_per_period, period_seconds)

    return _rate_limiters[name]
