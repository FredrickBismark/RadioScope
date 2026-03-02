#!/usr/bin/env bash
# RadioScope — first-time setup script
set -e

echo "◉ RadioScope Setup"
echo "===================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install with: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PYTHON_VERSION found"

# Check VLC
if ! command -v vlc &> /dev/null; then
    echo "⚠ VLC not found. Installing..."
    sudo apt install -y vlc
else
    echo "✓ VLC found"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "→ Creating virtual environment..."
    python3 -m venv venv
fi
echo "✓ Virtual environment ready"

# Activate and install deps
source venv/bin/activate
echo "→ Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Create .env if needed
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "→ Created .env from template"
    echo "  Edit .env to add your ANTHROPIC_API_KEY for AI features (optional)"
else
    echo "✓ .env already exists"
fi

# Create data directory
mkdir -p data
echo "✓ Data directory ready"

echo ""
echo "===================="
echo "✓ Setup complete!"
echo ""
echo "To run RadioScope:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "For AI station discovery, add your API key to .env"
