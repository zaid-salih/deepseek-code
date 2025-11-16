# deepseek-code/final_test.py
#!/usr/bin/env python3
"""Final comprehensive test of DeepSeek-Code"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_all_components():
    """Test all major components"""
    print("🚀 DeepSeek-Code Final Test")
    print("=" * 50)
    
    tests = [
        ("Core AI Engine", test_ai_engine),
        ("Team Management", test_team_management),
        ("File Operations", test_file_operations),
        ("Configuration", test_configuration),
        ("CLI Interface", test_cli_interface),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(success for _, success in results)
    return all_passed

def test_ai_engine():
    """Test AI engine functionality"""
    try:
        from deepseek_code.core.team_manager import TeamManager
        from deepseek_code.core.ai_engine import DeepSeekAI
        
        team_manager = TeamManager()
        team_config = team_manager._load_team_config()
        
        if not team_config:
            print("❌ AI Engine: No team config")
            return False
        
        api_key = team_manager.decrypt_api_key(team_config["api_key"])
        ai_engine = DeepSeekAI(api_key)
        
        # Test a simple completion
        test_messages = [{"role": "user", "content": "Say 'Hello World'"}]
        response = list(ai_engine.chat_completion(test_messages, stream=False))
        
        if response and len(response[0]) > 0:
            print("✅ AI Engine: Working")
            return True
        else:
            print("❌ AI Engine: No response")
            return False
            
    except Exception as e:
        print(f"❌ AI Engine: {e}")
        return False

def test_team_management():
    """Test team management"""
    try:
        from deepseek_code.core.team_manager import TeamManager
        
        team_manager = TeamManager()
        team_config = team_manager._load_team_config()
        
        if not team_config:
            print("❌ Team Management: No config")
            return False
        
        active_user = team_manager.get_active_user()
        if active_user and 'username' in active_user:
            print(f"✅ Team Management: Active user '{active_user['username']}'")
            return True
        else:
            print("❌ Team Management: No active user")
            return False
            
    except Exception as e:
        print(f"❌ Team Management: {e}")
        return False

def test_file_operations():
    """Test file operations"""
    try:
        from deepseek_code.core.file_manager import FileManager
        
        file_manager = FileManager()
        project_info = file_manager.discover_project_structure(max_files=5)
        
        if project_info and 'files' in project_info:
            print(f"✅ File Operations: Found {len(project_info['files'])} files")
            return True
        else:
            print("❌ File Operations: No project info")
            return False
            
    except Exception as e:
        print(f"❌ File Operations: {e}")
        return False

def test_configuration():
    """Test configuration system"""
    try:
        from deepseek_code.core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config_info = config_manager.get_config_info()
        
        if config_info['team_config_exists'] and config_info['usage_log_exists']:
            print("✅ Configuration: All config files present")
            return True
        else:
            print("❌ Configuration: Missing config files")
            return False
            
    except Exception as e:
        print(f"❌ Configuration: {e}")
        return False

def test_cli_interface():
    """Test CLI interface"""
    try:
        # Test that we can import the working main
        from deepseek_code.cli.working_main import app
        print("✅ CLI Interface: Working main imports correctly")
        return True
    except Exception as e:
        print(f"❌ CLI Interface: {e}")
        return False

if __name__ == "__main__":
    success = test_all_components()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! DeepSeek-Code is fully operational! 🎉")
        print("\n🚀 You can now use:")
        print("  python -m deepseek_code.cli.working_main chat")
        print("  python -m deepseek_code.cli.working_main analyze <file>")
        print("  python -m deepseek_code.cli.working_main team-info")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
    
    sys.exit(0 if success else 1)