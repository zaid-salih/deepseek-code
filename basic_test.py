# deepseek-code/basic_test.py
#!/usr/bin/env python3
"""Basic functionality test"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """Test basic module imports"""
    print("🔧 Testing Basic Imports...")
    
    modules_to_test = [
        ("core.ai_engine", "DeepSeekAI"),
        ("core.team_manager", "TeamManager"),
        ("core.file_manager", "FileManager"),
        ("core.config_manager", "ConfigManager"),
        ("cli.terminal_ui", "TerminalUI"),
    ]
    
    all_passed = True
    for module_path, class_name in modules_to_test:
        try:
            module = __import__(f"deepseek_code.{module_path}", fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_path}.{class_name}")
        except Exception as e:
            print(f"❌ {module_path}.{class_name}: {e}")
            all_passed = False
    
    return all_passed

def test_configuration():
    """Test configuration system"""
    print("\n🔧 Testing Configuration...")
    try:
        from deepseek_code.core.config_manager import ConfigManager
        from deepseek_code.core.team_manager import TeamManager
        
        config_manager = ConfigManager()
        team_manager = TeamManager()
        
        # Check if configuration exists
        config_info = config_manager.get_config_info()
        team_config = team_manager._load_team_config()
        
        print(f"✅ Config directory: {config_info['config_dir']}")
        print(f"✅ Team: {team_config.get('team_name', 'Unknown')}")
        print(f"✅ Users: {len(team_config.get('users', []))}")
        
        # Test API key (without making actual API call)
        api_key = team_manager.decrypt_api_key(team_config["api_key"])
        if api_key and api_key.startswith("sk-"):
            print("✅ API key: Valid format")
        else:
            print("⚠️  API key: May need setup")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    print("🚀 DeepSeek-Code Basic Test")
    print("=" * 40)
    
    imports_ok = test_basic_imports()
    config_ok = test_configuration()
    
    print("\n" + "=" * 40)
    if imports_ok and config_ok:
        print("✅ All basic tests passed!")
        print("\n🎯 You can now use the system!")
        print("\nTry these commands:")
        print("  python -m deepseek_code.cli.main chat")
        print("  python -m deepseek_code.cli.main analyze src/main.py")
        print("  python -m deepseek_code.cli.main team workflow-status")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    return imports_ok and config_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)