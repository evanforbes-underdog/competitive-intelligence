"""Email sending functionality using Gmail SMTP."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from ..utils.error_handler import retry_with_backoff


class EmailSender:
    """Send email reports via Gmail SMTP."""

    def __init__(self, config, logger, username: str, password: str):
        """Initialize email sender.

        Args:
            config: Configuration object
            logger: Logger instance
            username: Gmail username
            password: Gmail app password
        """
        self.config = config
        self.logger = logger
        self.username = username
        self.password = password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    @retry_with_backoff(max_retries=3, base_delay=60)
    def send_report(self, html_content: str, subject: str, recipients: List[str]) -> bool:
        """Send HTML email report.

        Args:
            html_content: HTML content of the email
            subject: Email subject line
            recipients: List of recipient email addresses

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            self.logger.info(f"Sending report to {len(recipients)} recipients")

            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.config.get('reporting.email.from_name', 'Competitive Intelligence Bot')} <{self.username}>"
            message['To'] = ', '.join(recipients)

            # Create plain text version (fallback)
            text_content = self._html_to_text(html_content)

            # Attach both versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')

            message.attach(part1)
            message.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)

            self.logger.info("Email sent successfully")
            return True

        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"Email authentication failed: {e}")
            raise

        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            raise

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text (simple version).

        Args:
            html: HTML content

        Returns:
            Plain text version
        """
        # Simple HTML to text conversion
        from html.parser import HTMLParser
        import re

        class HTMLToText(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []

            def handle_data(self, data):
                self.text.append(data)

            def get_text(self):
                return ' '.join(self.text)

        parser = HTMLToText()
        parser.feed(html)
        text = parser.get_text()

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def test_connection(self) -> bool:
        """Test SMTP connection and authentication.

        Returns:
            True if connection successful
        """
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                self.logger.info("Email connection test successful")
                return True

        except Exception as e:
            self.logger.error(f"Email connection test failed: {e}")
            return False
