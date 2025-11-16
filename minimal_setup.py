# deepseek-code/minimal_setup.py
#!/usr/bin/env python3
"""Minimal setup without external dependencies"""

import os
import json
import sys
from pathlib import Path

def create_config_structure():
    """Create the basic configuration structure"""
    config_dir = Path.home() / ".deepseek-code"
    config_dir.mkdir(exist_ok=True)
    
    print(f"📁 Creating configuration directory: {config_dir}")
    
    # Create subdirectories
    directories = [
        "backups",
        "refactoring_backups", 
        "templates",
        "code_reviews"
    ]
    
    for dir_name in directories:
        (config_dir / dir_name).mkdir(exist_ok=True)
        print(f"  └── {dir_name}/")
    
    return config_dir

def create_team_config(config_dir):
    """Create a basic team configuration"""
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
                "preferences": {
                    "theme": "dark",
                    "default_language": "python",
                    "code_style": "pep8",
                    "auto_save": True,
                    "max_file_size": 10000
                },
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-01T00:00:00Z"
            },
            {
                "user_id": "user_dev_002",
                "username": "developer1", 
                "role": "member",
                "preferences": {
                    "theme": "dark",
                    "default_language": "python",
                    "code_style": "pep8", 
                    "auto_save": True,
                    "max_file_size": 10000
                },
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-01T00:00:00Z"
            },
            {
                "user_id": "user_dev_003",
                "username": "developer2",
                "role": "member", 
                "preferences": {
                    "theme": "dark",
                    "default_language": "python",
                    "code_style": "pep8",
                    "auto_save": True,
                    "max_file_size": 10000
                },
                "created_at": "2024-01-01T00:00:00Z", 
                "last_active": "2024-01-01T00:00:00Z"
            }
        ]
    }
    
    config_file = config_dir / "team_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(team_config, f, indent=2)
    
    print(f"📄 Created: team_config.json")
    return config_file

def create_user_preferences(config_dir, team_config):
    """Create user preference files"""
    for user in team_config["users"]:
        user_id = user["user_id"]
        pref_file = config_dir / f"user_preferences_{user_id}.json"
        
        with open(pref_file, 'w', encoding='utf-8') as f:
            json.dump(user["preferences"], f, indent=2)
        
        print(f"👤 Created: user_preferences_{user_id}.json")

def create_usage_log(config_dir):
    """Create empty usage log"""
    usage_log = {}
    
    usage_file = config_dir / "usage_log.json"
    with open(usage_file, 'w', encoding='utf-8') as f:
        json.dump(usage_log, f, indent=2)
    
    print(f"📊 Created: usage_log.json")
    return usage_file

def create_example_templates(config_dir):
    """Create example project templates"""
    templates_dir = config_dir / "templates"
    
    # Python project template
    python_template = {
        "name": "python-basic",
        "description": "Basic Python project template",
        "created_by": "system",
        "created_at": "2024-01-01T00:00:00Z",
        "files": ["main.py", "requirements.txt", "README.md"],
        "metadata": {"language": "python", "type": "basic"}
    }
    
    template_dir = templates_dir / "python-basic"
    template_dir.mkdir(exist_ok=True)
    
    # Save template info
    with open(template_dir / "template.json", 'w', encoding='utf-8') as f:
        json.dump(python_template, f, indent=2)
    
    # Create template files
    with open(template_dir / "main.py", 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
        """Main application module"""

        def main():
            """Main function"""
            print("Hello from DeepSeek-Code template!")
            
        if __name__ == "__main__":
            main()
        ''')
    
    with open(template_dir / "requirements.txt", 'w', encoding='utf-8') as f:
        f.write('''deepseek-code>=1.0.0
        ''')
    
    with open(template_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write('''# Python Project

        Project created with DeepSeek-Code template.

        ## Features
        - Basic Python structure
        - Ready for development

        ## Usage
        ```bash
        python main.py
        ```
        ''')

    print(f"📁 Created example template: python-basic/")

    def main():
        """Main setup function"""
        print("🚀 DeepSeek-Code Minimal Setup")
        print("=" * 40)
        try:
            # Create directory structure
            config_dir = create_config_structure()
            
            # Create configuration files
            team_config_file = create_team_config(config_dir)
            
            # Load team config for user preferences
            with open(team_config_file, 'r', encoding='utf-8') as f:
                team_config = json.load(f)
            
            create_user_preferences(config_dir, team_config)
            create_usage_log(config_dir)
            create_example_templates(config_dir)
            
            print("\n✅ Configuration structure created successfully!")
            print(f"\n📁 Configuration location: {config_dir}")
            
            print("\n🔧 Next steps:")
            print("1. Edit ~/.deepseek-code/team_config.json")
            print("2. Replace 'YOUR_API_KEY_HERE' with your DeepSeek API key")
            print("3. Install dependencies: pip install -e .")
            print("4. Run: deepseek-code chat")
            
            # Show the created structure
            print(f"\n📁 Final structure:")
            for item in config_dir.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(config_dir)
                    print(f"   📄 {rel_path}")
                elif item.is_dir() and item != config_dir:
                    rel_path = item.relative_to(config_dir)
                    print(f"   📁 {rel_path}/")
                    
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False

        return True

    if name == "main":
    success = main()
    sys.exit(0 if success else 1)
