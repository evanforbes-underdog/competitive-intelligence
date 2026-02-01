#!/usr/bin/env python3
"""Verify system installation and configuration."""
import sys
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check(condition, message):
    """Print check result."""
    if condition:
        print(f"{GREEN}✓{RESET} {message}")
        return True
    else:
        print(f"{RED}✗{RESET} {message}")
        return False

def warn(message):
    """Print warning."""
    print(f"{YELLOW}⚠{RESET} {message}")

def main():
    """Run verification checks."""
    print("=" * 60)
    print("Competitive Intelligence System - Installation Verification")
    print("=" * 60)

    checks_passed = 0
    total_checks = 0

    # Check 1: Project structure
    print("\n1. Checking project structure...")
    total_checks += 1
    project_root = Path(__file__).parent.parent

    required_dirs = [
        'config', 'src', 'scripts', 'data', 'docs',
        'src/collectors', 'src/processors', 'src/database',
        'src/reporting', 'src/utils'
    ]

    structure_ok = True
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            print(f"   Missing directory: {dir_name}")
            structure_ok = False

    if check(structure_ok, "Project structure"):
        checks_passed += 1

    # Check 2: Configuration files
    print("\n2. Checking configuration files...")
    total_checks += 1

    config_files = [
        'config/config.yaml',
        '.env.example',
        'requirements.txt',
        'README.md'
    ]

    config_ok = True
    for file_name in config_files:
        file_path = project_root / file_name
        if not file_path.exists():
            print(f"   Missing file: {file_name}")
            config_ok = False

    if check(config_ok, "Configuration files"):
        checks_passed += 1

    # Check 3: Python version
    print("\n3. Checking Python version...")
    total_checks += 1

    py_version = sys.version_info
    version_ok = py_version.major == 3 and py_version.minor >= 8

    if check(version_ok, f"Python version ({py_version.major}.{py_version.minor}.{py_version.micro})"):
        checks_passed += 1
    else:
        print(f"   Requires Python 3.8+, found {py_version.major}.{py_version.minor}.{py_version.micro}")

    # Check 4: Virtual environment
    print("\n4. Checking virtual environment...")
    total_checks += 1

    venv_exists = (project_root / 'venv').exists()
    if check(venv_exists, "Virtual environment exists"):
        checks_passed += 1
    else:
        warn("Run './scripts/setup.sh' to create virtual environment")

    # Check 5: Dependencies
    print("\n5. Checking dependencies...")
    total_checks += 1

    required_packages = [
        'anthropic', 'requests', 'dotenv', 'yaml', 'sqlalchemy',
        'bs4', 'lxml', 'jinja2', 'colorlog'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if check(len(missing_packages) == 0, "All dependencies installed"):
        checks_passed += 1
    else:
        print(f"   Missing packages: {', '.join(missing_packages)}")
        warn("Run 'pip install -r requirements.txt' to install dependencies")

    # Check 6: Environment variables
    print("\n6. Checking environment variables...")
    total_checks += 1

    env_file = project_root / '.env'
    env_exists = env_file.exists()

    if check(env_exists, ".env file exists"):
        checks_passed += 1
    else:
        warn("Copy .env.example to .env and add your API keys")

    # Check 7: Source files
    print("\n7. Checking source files...")
    total_checks += 1

    required_files = [
        'src/main.py',
        'src/collectors/newsapi_collector.py',
        'src/processors/summarizer.py',
        'src/database/models.py',
        'src/reporting/report_generator.py',
        'src/utils/config_loader.py'
    ]

    files_ok = True
    for file_name in required_files:
        file_path = project_root / file_name
        if not file_path.exists():
            print(f"   Missing file: {file_name}")
            files_ok = False

    if check(files_ok, "Core source files"):
        checks_passed += 1

    # Check 8: Scripts are executable
    print("\n8. Checking script permissions...")
    total_checks += 1

    scripts = [
        'scripts/setup.sh',
        'scripts/test_email.py',
        'scripts/manual_run.py',
        'src/main.py'
    ]

    perms_ok = True
    for script in scripts:
        script_path = project_root / script
        if script_path.exists() and not script_path.stat().st_mode & 0o111:
            print(f"   Not executable: {script}")
            perms_ok = False

    if check(perms_ok, "Scripts are executable"):
        checks_passed += 1
    else:
        warn("Run 'chmod +x scripts/*.py scripts/*.sh src/main.py'")

    # Check 9: Database initialization
    print("\n9. Checking database...")
    total_checks += 1

    db_path = project_root / 'data' / 'competitive_intel.db'
    db_exists = db_path.exists()

    if check(db_exists, "Database exists"):
        checks_passed += 1
    else:
        warn("Database will be created on first run")

    # Check 10: Template file
    print("\n10. Checking email template...")
    total_checks += 1

    template_path = project_root / 'src' / 'reporting' / 'templates' / 'email_template.html'
    template_exists = template_path.exists()

    if check(template_exists, "Email template exists"):
        checks_passed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Verification Summary: {checks_passed}/{total_checks} checks passed")
    print("=" * 60)

    if checks_passed == total_checks:
        print(f"\n{GREEN}✓ Installation looks good!{RESET}")
        print("\nNext steps:")
        print("1. Configure API keys in .env file")
        print("2. Run: python3 scripts/test_email.py")
        print("3. Run: python3 scripts/manual_run.py")
        return True
    elif checks_passed >= total_checks - 2:
        print(f"\n{YELLOW}⚠ Installation mostly complete, check warnings above{RESET}")
        return True
    else:
        print(f"\n{RED}✗ Installation has issues, please review errors above{RESET}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
