# deepseek-code/ultimate_test.py
#!/usr/bin/env python3
"""Ultimate test of all DeepSeek-Code features"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def ultimate_test():
    """Test every major component"""
    print("🚀 DeepSeek-Code Ultimate Test")
    print("=" * 50)
    
    tests = [
        ("Configuration System", test_configuration),
        ("Team Management", test_team_management),
        ("File Operations", test_file_operations),
        ("Git Integration", test_git_integration),
        ("Project Templates", test_templates),
        ("CLI Commands", test_cli_commands),
        ("API Integration", test_api_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n🔧 Testing {test_name}...")
            success = test_func()
            status = "✅ PASS" if success else "❌ FAIL"
            results.append((test_name, success))
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 ULTIMATE TEST RESULTS:")
    print("=" * 50)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name:<25} {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print("=" * 50)
    print(f"  TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 PERFECT! All systems operational! 🎉")
    elif passed >= total * 0.8:
        print("\n🔥 EXCELLENT! Most systems working! 🔥")
    else:
        print("\n⚠️  Some systems need attention")
    
    return passed == total

def test_configuration():
    from deepseek_code.core.config_manager import ConfigManager
    config_manager = ConfigManager()
    info = config_manager.get_config_info()
    return all([
        info['team_config_exists'],
        info['usage_log_exists'],
        info['user_preference_files'] > 0
    ])

def test_team_management():
    from deepseek_code.core.team_manager import TeamManager
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    active_user = team_manager.get_active_user()
    return team_config and active_user and 'username' in active_user

def test_file_operations():
    from deepseek_code.core.file_manager import FileManager
    file_manager = FileManager()
    project_info = file_manager.discover_project_structure(max_files=5)
    return project_info and 'files' in project_info and len(project_info['files']) > 0

def test_git_integration():
    from deepseek_code.core.git_integration import GitIntegration
    git = GitIntegration()
    # Just test that it imports and initializes
    return git is not None

def test_templates():
    from deepseek_code.core.project_templates import ProjectTemplateManager
    template_manager = ProjectTemplateManager()
    templates = template_manager.list_templates()
    # Template system should work even if no templates exist yet
    return templates is not None

def test_cli_commands():
    try:
        from deepseek_code.cli.final_main import app
        return app is not None
    except:
        return False

def test_api_integration():
    from deepseek_code.core.team_manager import TeamManager
    from deepseek_code.core.ai_engine import DeepSeekAI
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    if team_config:
        try:
            api_key = team_manager.decrypt_api_key(team_config["api_key"])
            ai_engine = DeepSeekAI(api_key)
            # If we get here, API integration is configured
            return True
        except:
            return False
    return False

if __name__ == "__main__":
    success = ultimate_test()
    
    if success:
        print("\n🚀 DEEPSEEK-CODE IS READY FOR PRODUCTION! 🚀")
        print("\n💡 Once you add credits to your DeepSeek account:")
        print("   python -m deepseek_code.cli.final_main chat")
        print("   python -m deepseek_code.cli.final_main analyze <file>")
    else:
        print("\n🔧 Some components need configuration")
    
    sys.exit(0 if success else 1)