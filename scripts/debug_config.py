# deepseek-code/debug_config.py
#!/usr/bin/env python3
"""Debug configuration issues"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_config():
    """Debug configuration issues"""
    try:
        from deepseek_code.core.config_manager import ConfigManager
        from deepseek_code.core.team_manager import TeamManager
        
        print("🔧 Testing ConfigManager...")
        config_manager = ConfigManager()
        config_info = config_manager.get_config_info()
        print(f"✅ ConfigManager works: {config_info}")
        
        print("\n🔧 Testing TeamManager...")
        team_manager = TeamManager()
        team_config = team_manager._load_team_config()
        print(f"✅ TeamManager works: {team_config is not None}")
        
        if team_config:
            print(f"👥 Team: {team_config.get('team_name')}")
            print(f"👤 Users: {len(team_config.get('users', []))}")
            
            # Test API key decryption
            try:
                api_key = team_manager.decrypt_api_key(team_config["api_key"])
                print(f"🔑 API Key: {api_key[:10]}... (decrypted)")
            except Exception as e:
                print(f"❌ API Key decryption failed: {e}")
        
    except Exception as e:
        print(f"❌ Configuration debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_config()