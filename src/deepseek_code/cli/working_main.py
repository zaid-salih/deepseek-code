#!/usr/bin/env python3
"""DeepSeek-Code CLI Main Entry Point - Working Version"""

import os
import sys
import typer
from typing import Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from deepseek_code.core.ai_engine import DeepSeekAI
from deepseek_code.core.team_manager import TeamManager
from deepseek_code.core.file_manager import FileManager
from deepseek_code.core.config_manager import ConfigManager
from deepseek_code.cli.terminal_ui import TerminalUI
from deepseek_code.cli.auth_setup import first_time_setup

app = typer.Typer(
    name="deepseek-code",
    help="🚀 AI-Powered CLI IDE with DeepSeek integration",
    rich_markup_mode="rich"
)

ui = TerminalUI()

@app.command()
def setup():
    """Run first-time setup wizard"""
    first_time_setup(ui)

@app.command()
def chat():
    """Start interactive chat session"""
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        ui.display_error("Team configuration not found. Please run 'deepseek-code setup' first.")
        return
    
    active_user = team_manager.get_active_user()
    if not active_user:
        ui.display_error("No active user found.")
        return
    
    try:
        api_key = team_manager.decrypt_api_key(team_config["api_key"])
        ai_engine = DeepSeekAI(api_key)
    except Exception as e:
        ui.display_error(f"API key issue: {e}")
        return
    
    file_manager = FileManager()
    
    ui.display_welcome()
    ui.display_success(f"Active user: {active_user['username']}")
    
    # Show project overview
    project_info = file_manager.discover_project_structure()
    ui.console.print(f"📁 Project: {project_info['root']}")
    ui.console.print(f"📄 Files: {len(project_info['files'])}")
    
    conversation_history = [
        {
            "role": "system",
            "content": f"You are DeepSeek-Code, an expert AI assistant for software development. Current project: {project_info['root']} with {len(project_info['files'])} files."
        }
    ]
    
    ui.display_success("Ready for questions! Type 'quit' to exit.")
    
    while True:
        try:
            user_input = ui.prompt_user_input("Ask DeepSeek:")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            # Add user message to history
            conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Display AI response with streaming
            ui.console.print()
            with ui.console.status("[bold green]Thinking...[/bold green]"):
                try:
                    response_text = ""
                    for chunk in ai_engine.chat_completion(
                        conversation_history[-10:],  # Keep last 10 messages for context
                        stream=True
                    ):
                        response_text += chunk
                        ui.console.print(chunk, end="")
                    
                    ui.console.print()
                    
                    # Add AI response to history
                    conversation_history.append({
                        "role": "assistant", 
                        "content": response_text
                    })
                    
                except Exception as e:
                    ui.display_error(f"AI request failed: {e}")
                    break
            
        except KeyboardInterrupt:
            ui.console.print("\n[yellow]Session interrupted. Use 'quit' to exit properly.[/yellow]")
        except Exception as e:
            ui.display_error(f"An error occurred: {e}")

@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="File to analyze"),
    language: Optional[str] = typer.Option(None, help="Programming language")
):
    """Analyze a specific file"""
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        ui.display_error("Team configuration not found. Please run 'deepseek-code setup' first.")
        return
    
    try:
        api_key = team_manager.decrypt_api_key(team_config["api_key"])
        ai_engine = DeepSeekAI(api_key)
    except Exception as e:
        ui.display_error(f"API key issue: {e}")
        return
    
    file_manager = FileManager()
    
    content = file_manager.read_file(file_path)
    if not content:
        ui.display_error(f"Could not read file: {file_path}")
        return
    
    with ui.console.status("[bold green]Analyzing code...[/bold green]"):
        try:
            analysis = ai_engine.analyze_code(content, language)
            ui.display_chat_message("assistant", analysis["analysis"])
        except Exception as e:
            ui.display_error(f"Analysis failed: {e}")

@app.command()
def config_check():
    """Check system configuration"""
    config_manager = ConfigManager()
    team_manager = TeamManager()
    
    config_info = config_manager.get_config_info()
    team_config = team_manager._load_team_config()
    
    ui.console.print("🔧 Configuration Status:")
    ui.console.print(f"📁 Config directory: {config_info['config_dir']}")
    ui.console.print(f"👥 Team: {team_config.get('team_name', 'Unknown')}")
    ui.console.print(f"👤 Users: {len(team_config.get('users', []))}")
    ui.console.print(f"🔑 API Key: {'✅ Set' if team_config.get('api_key') else '❌ Missing'}")

@app.command()
def team_info():
    """Display team information"""
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        ui.display_error("Team configuration not found. Please run 'deepseek-code setup' first.")
        return
    
    active_user = team_manager.get_active_user()
    
    from rich.table import Table
    table = Table(title="👥 Team Information")
    table.add_column("User", style="cyan")
    table.add_column("Role", style="white")
    table.add_column("Last Active", style="yellow")
    
    for user in team_config["users"]:
        role = user["role"]
        if user["user_id"] == active_user["user_id"]:
            role = f"🟢 {role}"
        
        table.add_row(
            user["username"],
            role,
            user.get("last_active", "Unknown").split('T')[0]
        )
    
    ui.console.print(table)

if __name__ == "__main__":
    app()
