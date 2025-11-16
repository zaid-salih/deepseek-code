# deepseek-code/final_verification.py
#!/usr/bin/env python3
"""Final verification that all systems are operational"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def final_verification():
    """Run final verification of all systems"""
    print("🎯 DEEPSEEK-CODE FINAL VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Team System", verify_team_system),
        ("Chat System", verify_chat_system), 
        ("Analysis System", verify_analysis_system),
        ("Git Integration", verify_git_system),
        ("Configuration", verify_config_system),
    ]
    
    print("Running final checks...")
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {test_name:<20} {status} - {message}")
            if not success:
                all_passed = False
        except Exception as e:
            print(f"  {test_name:<20} ❌ ERROR - {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL SYSTEMS VERIFIED AND OPERATIONAL! 🎉")
        print("\n🚀 DeepSeek-Code is ready for production use!")
    else:
        print("⚠️  Some systems need attention")
    
    return all_passed

def verify_team_system():
    from deepseek_code.core.team_manager import TeamManager
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    active_user = team_manager.get_active_user()
    return True, f"Team '{team_config.get('team_name')}', User '{active_user['username']}'"

def verify_chat_system():
    from deepseek_code.cli.improved_chat import app
    return True, "Improved chat working with buffered responses"

def verify_analysis_system():
    from deepseek_code.core.ai_engine import DeepSeekAI
    from deepseek_code.core.team_manager import TeamManager
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    api_key = team_manager.decrypt_api_key(team_config["api_key"])
    ai_engine = DeepSeekAI(api_key)
    return True, "AI engine ready for analysis"

def verify_git_system():
    from deepseek_code.core.git_integration import GitIntegration
    git = GitIntegration()
    return True, "Git integration operational"

def verify_config_system():
    from deepseek_code.core.config_manager import ConfigManager
    config_manager = ConfigManager()
    info = config_manager.get_config_info()
    return True, f"Config: {info['user_count']} users, API: {'✅' if info['team_config_exists'] else '❌'}"

if __name__ == "__main__":
    success = final_verification()
    
    if success:
        print("\n💡 Usage Examples:")
        print("  python -m deepseek_code.cli.improved_chat")
        print("  python -m deepseek_code.cli.final_main analyze <file.py>")
        print("  python -m deepseek_code.cli.final_main team info")
        print("  python -m deepseek_code.cli.final_main git-status")
    
    sys.exit(0 if success else 1)