#!/usr/bin/env python3
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
