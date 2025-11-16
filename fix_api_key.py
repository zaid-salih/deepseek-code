# deepseek-code/fix_api_key.py
#!/usr/bin/env python3
"""Fix API key encryption issue"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def fix_api_key_encryption():
    """Fix the API key encryption issue"""
    from deepseek_code.core.team_manager import TeamManager
    from deepseek_code.core.config_manager import ConfigManager
    
    team_manager = TeamManager()
    config_manager = ConfigManager()
    
    team_config = team_manager._load_team_config()
    
    if not team_config:
        print("❌ No team configuration found")
        return False
    
    api_key = team_config.get("api_key", "")
    
    if not api_key:
        print("❌ No API key found in configuration")
        return False
    
    # Check if the API key is already encrypted
    if api_key.startswith("gAAAAA"):
        print("✅ API key is already encrypted")
        return True
    
    # Encrypt the API key
    try:
        encrypted_key = team_manager.encrypt_api_key(api_key)
        team_config["api_key"] = encrypted_key
        team_manager._save_team_config(team_config)
        print("✅ API key encrypted and saved")
        return True
    except Exception as e:
        print(f"❌ Failed to encrypt API key: {e}")
        return False

def main():
    print("🔑 Fixing API Key Encryption")
    print("=" * 40)
    
    if fix_api_key_encryption():
        print("\n✅ API key encryption fixed!")
        print("\n🔧 Testing decryption...")
        
        from deepseek_code.core.team_manager import TeamManager
        team_manager = TeamManager()
        team_config = team_manager._load_team_config()
        
        if team_config:
            try:
                api_key = team_manager.decrypt_api_key(team_config["api_key"])
                if api_key and api_key.startswith("sk-"):
                    print("✅ API key decryption successful!")
                    return True
                else:
                    print("❌ API key decryption failed - invalid format")
                    return False
            except Exception as e:
                print(f"❌ API key decryption failed: {e}")
                return False
    else:
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)