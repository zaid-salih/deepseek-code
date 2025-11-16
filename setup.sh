#!/bin/bash
# deepseek-code/setup.sh

echo "🚀 DeepSeek-Code Setup for Linux/macOS"
echo "======================================"

echo "Step 1: Initializing configuration..."
python3 initialize_config.py

if [ $? -ne 0 ]; then
    echo "❌ Initialization failed"
    exit 1
fi

echo "Step 2: Running setup wizard..."
python3 quick_setup.py

if [ $? -ne 0 ]; then
    echo "❌ Setup failed"
    exit 1
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "You can now use:"
echo "  deepseek-code chat"
echo "  deepseek-code analyze <file>"
echo "  deepseek-code team workflow-status"