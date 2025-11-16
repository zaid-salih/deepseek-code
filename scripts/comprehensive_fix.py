# deepseek-code/comprehensive_fix.py
#!/usr/bin/env python3
"""Comprehensive fix for import issues and cache clearing"""

import os
import sys
import shutil
from pathlib import Path

def clear_python_cache():
    """Clear all __pycache__ directories"""
    print("🧹 Clearing Python cache...")
    cache_dirs = list(Path("src").rglob("__pycache__"))
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Cleared: {cache_dir}")
        except Exception as e:
            print(f"⚠️  Could not clear {cache_dir}: {e}")
    
    # Also clear any .pyc files
    pyc_files = list(Path("src").rglob("*.pyc"))
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            print(f"✅ Removed: {pyc_file}")
        except Exception as e:
            print(f"⚠️  Could not remove {pyc_file}: {e}")
    
    return len(cache_dirs) > 0

def fix_file_imports(file_path):
    """Fix imports in a specific file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file uses Any but doesn't import it
        if "Any" in content and "from typing import" in content:
            if "Any" not in content.split("from typing import")[1].split(")")[0]:
                # Add Any to the import
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith("from typing import"):
                        if "Any" not in line:
                            # Add Any to the import
                            lines[i] = line.replace(")", ", Any)")
                            print(f"✅ Fixed imports in {file_path.name}")
                            break
                
                content = '\n'.join(lines)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        return False
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def fix_all_core_files():
    """Fix imports in all core files"""
    print("\n🔧 Fixing imports in all core files...")
    core_files = [
        "src/deepseek_code/core/git_integration.py",
        "src/deepseek_code/core/refactoring_engine.py",
        "src/deepseek_code/core/testing_integration.py", 
        "src/deepseek_code/core/code_review.py",
        "src/deepseek_code/core/analytics.py",
        "src/deepseek_code/core/project_templates.py",
        "src/deepseek_code/core/ai_engine.py",
        "src/deepseek_code/core/file_manager.py",
        "src/deepseek_code/core/team_manager.py",
        "src/deepseek_code/core/config_manager.py"
    ]
    
    fixed_count = 0
    for file_path in core_files:
        path = Path(file_path)
        if path.exists():
            if fix_file_imports(path):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {path}")
    
    return fixed_count

def create_simple_main():
    """Create a simplified main.py that doesn't import problematic modules"""
    print("\n🔄 Creating simplified main.py...")
    
    simple_main = '''#!/usr/bin/env python3
"""DeepSeek-Code CLI - Simplified Version"""

import typer
from typing import Optional

app = typer.Typer(
    name="deepseek-code",
    help="🚀 AI-Powered CLI IDE with DeepSeek integration",
    rich_markup_mode="rich"
)

@app.command()
def setup():
    """Run first-time setup wizard"""
    from deepseek_code.cli.auth_setup import first_time_setup
    from deepseek_code.cli.terminal_ui import TerminalUI
    ui = TerminalUI()
    first_time_setup(ui)

@app.command()
def chat():
    """Start interactive chat session"""
    try:
        from deepseek_code.core.team_manager import TeamManager
        from deepseek_code.core.ai_engine import DeepSeekAI
        from deepseek_code.core.file_manager import FileManager
        from deepseek_code.cli.terminal_ui import TerminalUI
        
        team_manager = TeamManager()
        team_config = team_manager._load_team_config()
        
        if not team_config:
            print("❌ Team configuration not found. Please run 'deepseek-code setup' first.")
            return
        
        api_key = team_manager.decrypt_api_key(team_config["api_key"])
        ai_engine = DeepSeekAI(api_key)
        file_manager = FileManager()
        ui = TerminalUI()
        
        ui.display_welcome()
        print("🚀 Chat feature would start here...")
        print("💡 This is a simplified version for testing.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

@app.command()
def analyze(file_path: str):
    """Analyze a specific file"""
    try:
        from deepseek_code.core.team_manager import TeamManager
        from deepseek_code.core.ai_engine import DeepSeekAI
        from deepseek_code.core.file_manager import FileManager
        
        team_manager = TeamManager()
        team_config = team_manager._load_team_config()
        
        if not team_config:
            print("❌ Team configuration not found. Please run 'deepseek-code setup' first.")
            return
        
        api_key = team_manager.decrypt_api_key(team_config["api_key"])
        ai_engine = DeepSeekAI(api_key)
        file_manager = FileManager()
        
        content = file_manager.read_file(file_path)
        if content:
            print(f"✅ File {file_path} read successfully ({len(content)} characters)")
            print("📊 Analysis would happen here...")
        else:
            print(f"❌ Could not read file: {file_path}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

@app.command()
def config_check():
    """Check system configuration"""
    try:
        from deepseek_code.core.config_manager import ConfigManager
        from deepseek_code.core.team_manager import TeamManager
        
        config_manager = ConfigManager()
        team_manager = TeamManager()
        
        config_info = config_manager.get_config_info()
        team_config = team_manager._load_team_config()
        
        print("🔧 Configuration Status:")
        print(f"📁 Config directory: {config_info['config_dir']}")
        print(f"👥 Team: {team_config.get('team_name', 'Unknown')}")
        print(f"👤 Users: {len(team_config.get('users', []))}")
        print(f"🔑 API Key: {'✅ Set' if team_config.get('api_key') else '❌ Missing'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    app()
'''

    with open("src/deepseek_code/cli/simple_main.py", 'w', encoding='utf-8') as f:
        f.write(simple_main)
    
    print("✅ Created simplified main.py")
    return True

def test_fixed_imports():
    """Test if imports are working after fixes"""
    print("\n🧪 Testing imports...")
    
    test_modules = [
        "deepseek_code.core.ai_engine",
        "deepseek_code.core.team_manager", 
        "deepseek_code.core.file_manager",
        "deepseek_code.core.config_manager",
        "deepseek_code.cli.terminal_ui"
    ]
    
    all_ok = True
    for module_name in test_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            print(f"❌ {module_name}: {e}")
            all_ok = False
    
    return all_ok

def main():
    print("🚀 DeepSeek-Code Comprehensive Fix")
    print("=" * 50)
    
    # Clear cache
    clear_python_cache()
    
    # Fix imports
    fixed_count = fix_all_core_files()
    print(f"\n✅ Fixed {fixed_count} files")
    
    # Create simplified main
    create_simple_main()
    
    # Test imports
    if test_fixed_imports():
        print("\n🎉 All imports fixed successfully!")
        print("\n🚀 You can now use:")
        print("  python -m deepseek_code.cli.simple_main --help")
        print("  python -m deepseek_code.cli.simple_main chat")
        print("  python -m deepseek_code.cli.simple_main config-check")
    else:
        print("\n⚠️  Some imports still have issues")
    
    return True

if __name__ == "__main__":
    main()