#!/bin/bash
# deepseek-code/installers/install.sh
echo "🚀 Installing DeepSeek-Code..."

# Detect platform
PLATFORM=$(uname -s)

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+ first."
    exit 1
fi

# Download and run Python installer
curl -fsSL https://raw.githubusercontent.com/yourusername/deepseek-code/main/installers/install.py -o /tmp/deepseek_install.py
python3 /tmp/deepseek_install.py

# Cleanup
rm -f /tmp/deepseek_install.py