# deepseek-code/quick_test.py
#!/usr/bin/env python3
"""Quick test of core functionality"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def quick_test():
    """Run a quick test of core functionality"""
    print("🚀 Quick DeepSeek-Code Test")
    print("=" * 40)
    
    try:
        from deepseek_code.core.team_manager import TeamManager
        from deepseek_code.core.ai_engine import DeepSeekAI
        from deepseek_code.core.file_manager import FileManager
        from deepseek_code.cli.terminal_ui import TerminalUI
        
        print("✅ Core imports successful")
        
        # Test team manager
        team_manager = TeamManager()
        team_config = team_manager._load_team_config()
        
        if team_config:
            print(f"✅ Team config loaded: {team_config.get('team_name')}")
            
            # Test API key
            try:
                api_key = team_manager.decrypt_api_key(team_config["api_key"])
                if api_key and api_key.startswith("sk-"):
                    print("✅ API key valid")
                    
                    # Test AI engine
                    try:
                        ai_engine = DeepSeekAI(api_key)
                        print("✅ AI engine initialized")
                        
                        # Test file manager
                        file_manager = FileManager()
                        project_info = file_manager.discover_project_structure(max_files=5)
                        print(f"✅ File manager working: {len(project_info['files'])} files found")
                        
                        # Test terminal UI
                        ui = TerminalUI()
                        print("✅ Terminal UI initialized")
                        
                        print("\n🎉 All core components working!")
                        return True
                        
                    except Exception as e:
                        print(f"❌ AI engine test failed: {e}")
                        return False
                else:
                    print("❌ API key invalid format")
                    return False
            except Exception as e:
                print(f"❌ API key decryption failed: {e}")
                return False
        else:
            print("❌ No team config found")
            return False
            
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🚀 System is ready! Try: python -m deepseek_code.cli.working_main chat")
    else:
        print("\n⚠️  Some issues found. Check the output above.")
    
    sys.exit(0 if success else 1)