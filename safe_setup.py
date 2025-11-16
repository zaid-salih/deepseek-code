# deepseek-code/safe_setup.py
#!/usr/bin/env python3
"""Safe setup that handles missing dependencies"""

import os
import json
import sys
from pathlib import Path

def check_dependencies():
    """Check for required dependencies"""
    missing_deps = []
    
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import rich
    except ImportError:
        missing_deps.append("rich") 
    
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        missing_deps.append("cryptography")
    
    return missing_deps

def create_basic_config():
    """Create basic config without external dependencies"""
    config_dir = Path.home() / ".deepseek-code"
    config_dir.mkdir(exist_ok=True)
    
    print(f"📁 Creating configuration directory: {config_dir}")
    
    # Create directory structure
    dirs = ["backups", "refactoring_backups", "templates", "code_reviews"]
    for dir_name in dirs:
        (config_dir / dir_name).mkdir(exist_ok=True)
        print(f"  └── {dir_name}/")
    
    # Create basic team config (without encryption)
    team_config = {
        "team_name": "MyDevTeam",
        "team_id": "team_default_001", 
        "api_key": "YOUR_API_KEY_HERE",  # User will replace this
        "created_date": "2024-01-01T00:00:00Z",
        "active_user": "user_admin_001",
        "users": [
            {
                "user_id": "user_admin_001",
                "username": "admin",
                "role": "admin",
                "preferences": {},
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-01T00:00:00Z"
            },
            {
                "user_id": "user_dev_002", 
                "username": "developer1",
                "role": "member", 
                "preferences": {},
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-01T00:00:00Z"
            },
            {
                "user_id": "user_dev_003",
                "username": "developer2", 
                "role": "member",
                "preferences": {},
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-01T00:00:00Z"
            }
        ]
    }
    
    # Save config files
    with open(config_dir / "team_config.json", 'w') as f:
        json.dump(team_config, f, indent=2)
    print("📄 Created: team_config.json")
    
    with open(config_dir / "usage_log.json", 'w') as f:
        json.dump({}, f, indent=2)
    print("📊 Created: usage_log.json")
    
    # Create user preference files
    for user in team_config["users"]:
        pref_file = config_dir / f"user_preferences_{user['user_id']}.json"
        with open(pref_file, 'w') as f:
            json.dump(user["preferences"], f, indent=2)
        print(f"👤 Created: user_preferences_{user['user_id']}.json")
    
    return config_dir

def main():
    print("🚀 DeepSeek-Code Safe Setup")
    print("=" * 40)
    
    # Check dependencies
    missing_deps = check_dependencies()
    
    if missing_deps:
        print("⚠️  Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 You can install them with: pip install " + " ".join(missing_deps))
        print("   Or run: pip install -e .")
        print("\n🔄 Continuing with basic setup...")
    
    # Create configuration
    config_dir = create_basic_config()
    
    print(f"\n✅ Basic configuration created at: {config_dir}")
    print("\n🎯 Next steps:")
    print("1. Install dependencies: pip install -e .")
    print("2. Edit ~/.deepseek-code/team_config.json")
    print("3. Replace 'YOUR_API_KEY_HERE' with your DeepSeek API key")
    print("4. Run: deepseek-code chat")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)