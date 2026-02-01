#!/bin/bash
# Setup script for competitive intelligence system

set -e

echo "========================================="
echo "Competitive Intelligence System Setup"
echo "========================================="

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Project directory: $PROJECT_DIR"

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created. Please edit it with your API keys."
else
    echo ""
    echo ".env file already exists"
fi

# Create data directories
echo ""
echo "Creating data directories..."
mkdir -p data/logs
mkdir -p data/reports

# Initialize database
echo ""
echo "Initializing database..."
python3 src/database/migrations.py "$(pwd)/data/competitive_intel.db"

# Set executable permissions
echo ""
echo "Setting executable permissions..."
chmod +x src/main.py
chmod +x scripts/*.py
chmod +x scripts/*.sh

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - ANTHROPIC_API_KEY"
echo "   - NEWSAPI_KEY"
echo "   - GMAIL_USERNAME"
echo "   - GMAIL_APP_PASSWORD"
echo ""
echo "2. Test the configuration:"
echo "   python3 scripts/test_email.py"
echo ""
echo "3. Run a manual test:"
echo "   python3 scripts/manual_run.py"
echo ""
echo "4. Set up cron job (optional):"
echo "   crontab -e"
echo "   Add: 0 8 * * 1 $(pwd)/venv/bin/python3 $(pwd)/src/main.py"
echo ""
