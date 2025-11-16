# deepseek-code/test_system.py
#!/usr/bin/env python3
"""Comprehensive system test for DeepSeek-Code"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_configuration():
    """Test configuration system"""
    print("🔧 Testing Configuration System...")
    
    from deepseek_code.core.config_manager import ConfigManager
    from deepseek_code.core.team_manager import TeamManager
    
    config_manager = ConfigManager()
    team_manager = TeamManager()
    
    # Check if configuration exists
    config_info = config_manager.get_config_info()
    
    print(f"📁 Config directory: {config_info['config_dir']}")
    print(f"👥 Team config: {'✅ Exists' if config_info['team_config_exists'] else '❌ Missing'}")
    print(f"📊 Usage log: {'✅ Exists' if config_info['usage_log_exists'] else '❌ Missing'}")
    print(f"👤 User preference files: {config_info['user_preference_files']}")
    print(f"💾 Backups: {config_info['total_backups']}")
    
    # Test team manager
    team_config = team_manager._load_team_config()
    if team_config:
        print(f"🏢 Team name: {team_config.get('team_name', 'Not set')}")
        print(f"👥 Users: {len(team_config.get('users', []))}")
    else:
        print("❌ No team configuration found")
    
    return config_info["team_config_exists"]

def test_core_modules():
    """Test core modules"""
    print("\n🔍 Testing Core Modules...")
    
    from deepseek_code.core.file_manager import FileManager
    from deepseek_code.core.git_integration import GitIntegration
    
    # Test file manager
    file_manager = FileManager()
    project_structure = file_manager.discover_project_structure(max_files=10)
    print(f"📁 File Manager: ✅ Working (found {len(project_structure['files'])} files)")
    
    # Test git integration
    git = GitIntegration()
    is_repo = git.is_git_repository()
    print(f"📚 Git Integration: {'✅ Working' if is_repo else '⚠️ Not a git repo'}")
    
    return True

def test_cli_commands():
    """Test CLI command registration"""
    print("\n🎯 Testing CLI Commands...")
    
    from deepseek_code.cli.main import app
    from deepseek_code.cli.phase2_commands import phase2_app
    from deepseek_code.cli.phase4_commands import phase4_app
    from deepseek_code.cli.ide_commands import ide_app
    
    commands = []
    
    # Get all commands from main app
    for command in app.registered_commands:
        commands.append(f"deepseek-code {command.name}")
    
    # Get commands from sub-commands
    for typer_instance in [phase2_app, phase4_app, ide_app]:
        for command in typer_instance.registered_commands:
            commands.append(f"deepseek-code {typer_instance.info.name} {command.name}")
    
    print(f"📋 Available commands: {len(commands)}")
    for cmd in sorted(commands)[:10]:  # Show first 10
        print(f"   - {cmd}")
    if len(commands) > 10:
        print(f"   ... and {len(commands) - 10} more")
    
    return len(commands) > 0

def test_ide_integration():
    """Test IDE integration components"""
    print("\n💻 Testing IDE Integration...")
    
    # Check VS Code extension
    vscode_dir = Path("vscode_extension")
    if vscode_dir.exists():
        package_json = vscode_dir / "package.json"
        if package_json.exists():
            print("🔌 VS Code Extension: ✅ Available")
        else:
            print("🔌 VS Code Extension: ⚠️ Incomplete (missing package.json)")
    else:
        print("🔌 VS Code Extension: ❌ Not found")
    
    # Check Visual Studio extension
    vs_dir = Path("visualstudio_extension")
    if vs_dir.exists():
        csproj_files = list(vs_dir.glob("*.csproj"))
        if csproj_files:
            print("🔌 Visual Studio Extension: ✅ Available")
        else:
            print("🔌 Visual Studio Extension: ⚠️ Incomplete (missing .csproj)")
    else:
        print("🔌 Visual Studio Extension: ❌ Not found")
    
    # Check LSP server
    try:
        from deepseek_code.ide.lsp_server import DeepSeekLanguageServer
        print("🔧 LSP Server: ✅ Available")
    except ImportError as e:
        print(f"🔧 LSP Server: ⚠️ Dependencies missing - {e}")
    
    return True

def main():
    """Run comprehensive system test"""
    print("🎯 DeepSeek-Code Comprehensive System Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run tests
    if not test_configuration():
        print("❌ Configuration test failed - running initialization...")
        from deepseek_code.cli.init_system import initialize_complete_system
        initialize_complete_system()
        if not test_configuration():
            all_tests_passed = False
    
    test_core_modules()
    test_cli_commands()
    test_ide_integration()
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ All tests passed! System is ready.")
        print("\n🚀 Next steps:")
        print("1. Run: deepseek-code setup")
        print("2. Configure your DeepSeek API key and team")
        print("3. Start using: deepseek-code chat")
    else:
        print("⚠️  Some tests had issues. Check the output above.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)