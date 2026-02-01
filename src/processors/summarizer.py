"""AI-powered summarization using Claude API."""
import anthropic
from typing import List, Dict
from ..utils.error_handler import retry_with_backoff, GracefulDegradation
from ..utils.rate_limiter import get_rate_limiter


class Summarizer:
    """Claude-powered article summarizer."""

    def __init__(self, config, logger, api_key: str):
        """Initialize summarizer.

        Args:
            config: Configuration object
            logger: Logger instance
            api_key: Anthropic API key
        """
        self.config = config
        self.logger = logger
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = config.get('processing.claude.model', 'claude-3-5-sonnet-20241022')
        self.max_tokens = config.get('processing.claude.max_tokens', 300)
        self.temperature = config.get('processing.claude.temperature', 0.3)
        self.batch_size = config.get('processing.claude.batch_size', 10)
        self.rate_limiter = get_rate_limiter("claude", 50, 60)  # 50 per minute

    def summarize_batch(self, articles: List[Dict]) -> List[Dict]:
        """Summarize a batch of articles.

        Args:
            articles: List of article dicts with 'title', 'content', 'url'

        Returns:
            List of dicts with 'url' and 'summary'
        """
        if not articles:
            return []

        # Process in batches
        results = []
        for i in range(0, len(articles), self.batch_size):
            batch = articles[i:i + self.batch_size]
            try:
                batch_results = self._process_batch(batch)
                results.extend(batch_results)
            except Exception as e:
                self.logger.warning(f"Batch summarization failed, falling back to extractive: {e}")
                # Fallback to extractive summarization
                for article in batch:
                    results.append({
                        'url': article['url'],
                        'summary': GracefulDegradation.extractive_summary(article['content'], 3)
                    })

        return results

    @retry_with_backoff(max_retries=2)
    def _process_batch(self, articles: List[Dict]) -> List[Dict]:
        """Process a single batch with Claude API.

        Args:
            articles: List of article dicts

        Returns:
            List of summary results
        """
        # Rate limiting
        self.rate_limiter.acquire()

        # Build prompt for batch processing
        prompt = self._build_batch_prompt(articles)

        self.logger.debug(f"Summarizing batch of {len(articles)} articles")

        # Call Claude API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens * len(articles),
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Parse response
        response_text = message.content[0].text
        results = self._parse_batch_response(response_text, articles)

        return results

    def _build_batch_prompt(self, articles: List[Dict]) -> str:
        """Build a prompt for batch summarization.

        Args:
            articles: List of article dicts

        Returns:
            Formatted prompt
        """
        prompt = """You are a competitive intelligence analyst. Summarize each of the following articles in 2-3 sentences, focusing on:
- Key business/product developments
- Marketing strategies or campaigns
- Partnership announcements
- Regulatory news
- Anything competitively relevant

Format your response as:
[1] Summary text here
[2] Summary text here
[3] Summary text here

Articles to summarize:

"""

        for idx, article in enumerate(articles, 1):
            title = article.get('title', 'No Title')
            content = article.get('content', '')[:1000]  # Limit content length

            prompt += f"\n[{idx}] Title: {title}\n"
            prompt += f"Content: {content}\n"
            prompt += "-" * 80 + "\n"

        return prompt

    def _parse_batch_response(self, response: str, articles: List[Dict]) -> List[Dict]:
        """Parse Claude's batch response.

        Args:
            response: Raw response text from Claude
            articles: Original articles for URL mapping

        Returns:
            List of summary results
        """
        results = []
        lines = response.strip().split('\n')

        current_summary = []
        current_idx = None

        for line in lines:
            line = line.strip()

            # Check if this is a new article marker
            if line.startswith('[') and ']' in line:
                # Save previous summary
                if current_idx is not None and current_summary:
                    summary_text = ' '.join(current_summary).strip()
                    if current_idx - 1 < len(articles):
                        results.append({
                            'url': articles[current_idx - 1]['url'],
                            'summary': summary_text
                        })

                # Start new summary
                try:
                    idx_str = line.split(']')[0].strip('[')
                    current_idx = int(idx_str)
                    # Get text after the marker
                    text_after_marker = line.split(']', 1)[1].strip()
                    current_summary = [text_after_marker] if text_after_marker else []
                except:
                    current_summary = []
            elif current_idx is not None and line:
                current_summary.append(line)

        # Save last summary
        if current_idx is not None and current_summary:
            summary_text = ' '.join(current_summary).strip()
            if current_idx - 1 < len(articles):
                results.append({
                    'url': articles[current_idx - 1]['url'],
                    'summary': summary_text
                })

        # Ensure we have a result for each article (fallback if parsing failed)
        if len(results) < len(articles):
            self.logger.warning(f"Only parsed {len(results)}/{len(articles)} summaries, using fallback")
            for i, article in enumerate(articles):
                if not any(r['url'] == article['url'] for r in results):
                    results.append({
                        'url': article['url'],
                        'summary': GracefulDegradation.extractive_summary(article['content'], 3)
                    })

        return results

    def summarize_single(self, title: str, content: str) -> str:
        """Summarize a single article.

        Args:
            title: Article title
            content: Article content

        Returns:
            Summary text
        """
        results = self.summarize_batch([{
            'url': 'single',
            'title': title,
            'content': content
        }])

        return results[0]['summary'] if results else GracefulDegradation.extractive_summary(content, 3)
