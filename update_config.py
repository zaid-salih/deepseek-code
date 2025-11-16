# deepseek-code/update_config.py
#!/usr/bin/env python3
"""Update configuration with API key"""

import json
import sys
from pathlib import Path

def update_api_key(api_key: str):
    """Update the team config with the actual API key"""
    config_dir = Path.home() / ".deepseek-code"
    config_file = config_dir / "team_config.json"
    
    if not config_file.exists():
        print("❌ Configuration file not found. Run safe_setup.py first.")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Update the API key
        config["api_key"] = api_key
        print(f"✅ Updated API key in configuration")
        
        # Save the updated config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_config.py <your_deepseek_api_key>")
        print("Get your API key from: https://platform.deepseek.com/api_keys")
        return False
    
    api_key = sys.argv[1]
    return update_api_key(api_key)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)