#!/bin/bash

# TruthProbe v4.0 Installation Script
# Complete setup with all dependencies

echo "🔧 Setting up TruthProbe v4.0 Enhanced Edition"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv truthprobe_env
source truthprobe_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
echo "Installing core dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"

# Create directory structure
echo "Creating directory structure..."
mkdir -p src/core src/utils src/interfaces tests examples dashboards integrations

# Make scripts executable
chmod +x run_dashboard.sh
chmod +x run_tests.sh

# Create .env file
echo "Creating environment configuration..."
cat > .env << EOL
# TruthProbe Configuration
TRUTHPROBE_VERSION=4.0.0
LOG_LEVEL=INFO
MAX_RESPONSE_LENGTH=5000
RISK_THRESHOLD_HIGH=0.7
RISK_THRESHOLD_MEDIUM=0.4

# API Keys (Add your own)
WIKIPEDIA_API_ENABLED=true
ARXIV_API_ENABLED=true

# Dashboard Settings
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8050
EOL

echo "✅ Installation complete!"
echo ""
echo "To activate the environment:"
echo "  source truthprobe_env/bin/activate"
echo ""
echo "To run the dashboard:"
echo "  python dashboard/realtime_monitor.py"
echo ""
echo "To run tests:"
echo "  pytest tests/"
