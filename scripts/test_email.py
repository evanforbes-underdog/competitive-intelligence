#!/usr/bin/env python3
"""Test email configuration and connectivity."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.config_loader import ConfigLoader
from utils.logger import Logger
from reporting.email_sender import EmailSender


def main():
    """Test email configuration."""
    print("=" * 60)
    print("Email Configuration Test")
    print("=" * 60)

    try:
        # Load config
        print("\n1. Loading configuration...")
        config = ConfigLoader()
        print("   ✓ Configuration loaded")

        # Set up logger
        logger = Logger.get_logger(__name__, None, 'INFO')

        # Get email credentials
        print("\n2. Checking email credentials...")
        gmail_user = config.get_env('GMAIL_USERNAME')
        gmail_pass = config.get_env('GMAIL_APP_PASSWORD')

        if not gmail_user or not gmail_pass:
            print("   ✗ Email credentials not configured in .env file")
            return False

        print(f"   ✓ Gmail username: {gmail_user}")

        # Initialize email sender
        print("\n3. Initializing email sender...")
        email_sender = EmailSender(config, logger, gmail_user, gmail_pass)
        print("   ✓ Email sender initialized")

        # Test connection
        print("\n4. Testing SMTP connection...")
        if email_sender.test_connection():
            print("   ✓ SMTP connection successful")
        else:
            print("   ✗ SMTP connection failed")
            return False

        # Send test email
        print("\n5. Sending test email...")
        recipients = config.get('reporting.email.recipients', [])

        if not recipients:
            print("   ✗ No recipients configured in config.yaml")
            return False

        test_html = """
        <html>
        <body>
            <h1>Competitive Intelligence System - Test Email</h1>
            <p>This is a test email from the competitive intelligence system.</p>
            <p>If you received this, your email configuration is working correctly!</p>
        </body>
        </html>
        """

        success = email_sender.send_report(
            test_html,
            "Test Email - Competitive Intelligence System",
            recipients
        )

        if success:
            print(f"   ✓ Test email sent to {', '.join(recipients)}")
            print("\n" + "=" * 60)
            print("All tests passed! Email configuration is working.")
            print("=" * 60)
            return True
        else:
            print("   ✗ Failed to send test email")
            return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
