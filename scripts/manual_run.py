#!/usr/bin/env python3
"""Manual test run without sending email."""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import CompetitiveIntelligenceSystem


def main():
    """Run the system without sending email."""
    print("=" * 80)
    print("Competitive Intelligence System - Manual Test Run")
    print("=" * 80)
    print("\nThis will collect articles and generate a report WITHOUT sending email.")
    print("The report will be saved to data/reports/\n")

    input("Press Enter to continue or Ctrl+C to cancel...")

    try:
        # Initialize system
        system = CompetitiveIntelligenceSystem()

        # Run collection
        print("\n" + "=" * 80)
        print("Step 1: Collecting Articles")
        print("=" * 80)
        articles = system._collect_articles()

        # Store articles
        print("\n" + "=" * 80)
        print("Step 2: Storing Articles")
        print("=" * 80)
        new_articles = system._store_articles(articles)

        # Process articles
        print("\n" + "=" * 80)
        print("Step 3: Processing Articles")
        print("=" * 80)
        system._process_articles(new_articles)

        # Generate report
        print("\n" + "=" * 80)
        print("Step 4: Generating Report")
        print("=" * 80)
        report, html_content = system._generate_report()

        # Save report to file
        report_dir = Path(__file__).parent.parent / 'data' / 'reports'
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f"manual_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"

        with open(report_file, 'w') as f:
            f.write(html_content)

        print(f"\n✓ Report saved to: {report_file}")

        # Print summary
        print("\n" + "=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"Articles collected: {system.metrics['articles_collected']}")
        print(f"New articles: {system.metrics['articles_new']}")
        print(f"Duplicates: {system.metrics['articles_duplicate']}")
        print(f"Summaries generated: {system.metrics['summaries_generated']}")

        if system.metrics['errors']:
            print(f"\nErrors encountered: {len(system.metrics['errors'])}")
            for error in system.metrics['errors']:
                print(f"  - {error}")

        print("\n" + "=" * 80)
        print("Manual run completed successfully!")
        print("=" * 80)
        print(f"\nOpen the report in your browser: file://{report_file}")

        return True

    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
