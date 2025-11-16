# deepseek-code/src/deepseek_code/cli/main.py
#!/usr/bin/env python3
"""DeepSeek-Code CLI Main Entry Point"""

import os
import sys
import typer
from typing import Optional
import logging
from .phase2_commands import phase2_app
from .ide_commands import ide_app
from .phase4_commands import phase4_app

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from deepseek_code.core.ai_engine import DeepSeekAI
from deepseek_code.core.team_manager import TeamManager
from deepseek_code.core.file_manager import FileManager
from deepseek_code.cli.terminal_ui import TerminalUI
from deepseek_code.cli.auth_setup import first_time_setup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
    
    api_key = team_manager.decrypt_api_key(team_config["api_key"])
    ai_engine = DeepSeekAI(api_key)
    file_manager = FileManager()
    
    ui.display_welcome()
    ui.display_team_info(team_config, active_user)
    
    # Show project overview
    project_info = file_manager.discover_project_structure()
    ui.display_project_info(project_info)
    
    conversation_history = [
        {
            "role": "system",
            "content": f"""You are DeepSeek-Code, an expert AI assistant for software development.

Current Project Context:
- Root: {project_info['root']}
- Files: {len(project_info['files'])} files
- File types: {', '.join(project_info['file_types'].keys())}

You have access to:
- Read and analyze project files
- Provide code suggestions and refactoring
- Help with debugging and testing
- Assist with git operations
- Support multiple programming languages

Always be concise, helpful, and focus on practical solutions."""
        }
    ]
    
    ui.display_success("Ready for questions! Type 'quit' to exit, 'files' to see project structure.")
    
    while True:
        try:
            user_input = ui.prompt_user_input()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'files':
                file_tree = file_manager.get_file_tree()
                ui.display_file_tree(file_tree)
                continue
            
            # Add user message to history
            conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Display AI response with streaming
            ui.console.print()
            with ui.console.status("[bold green]Thinking...[/bold green]"):
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
                
                # Track usage
                team_manager.track_usage(
                    active_user["user_id"],
                    "chat_completion",
                    len(response_text.split())  # Rough token estimate
                )
            
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
    
    api_key = team_manager.decrypt_api_key(team_config["api_key"])
    ai_engine = DeepSeekAI(api_key)
    file_manager = FileManager()
    
    content = file_manager.read_file(file_path)
    if not content:
        ui.display_error(f"Could not read file: {file_path}")
        return
    
    with ui.console.status("[bold green]Analyzing code...[/bold green]"):
        analysis = ai_engine.analyze_code(content, language)
    
    ui.display_chat_message("assistant", analysis["analysis"])

@app.command()
def switch_user(user_id: str):
    """Switch active user"""
    team_manager = TeamManager()
    
    if team_manager.switch_user(user_id):
        active_user = team_manager.get_active_user()
        ui.display_success(f"Switched to user: {active_user['username']}")
    else:
        ui.display_error(f"User {user_id} not found")

@app.command()
def team_info():
    """Display team information and usage"""
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        ui.display_error("Team configuration not found. Please run 'deepseek-code setup' first.")
        return
    
    active_user = team_manager.get_active_user()
    ui.display_team_info(team_config, active_user)
    
    # Show usage statistics
    usage = team_manager.get_team_usage()
    if usage:
        ui.console.print("\n[bold]📊 Recent Usage:[/bold]")
        for date, daily_usage in list(usage.items())[-3:]:  # Last 3 days
            ui.console.print(f"\n{date}:")
            for user_id, user_usage in daily_usage.items():
                username = next(
                    (u["username"] for u in team_config["users"] if u["user_id"] == user_id),
                    user_id
                )
                ui.console.print(f"  {username}: {user_usage['tokens_used']} tokens")

if __name__ == "__main__":
    app()

app.add_typer(phase2_app, name="advanced", help="Advanced code operations")
app.add_typer(ide_app, name="ide", help="IDE integration commands")
app.add_typer(phase4_app, name="team", help="Team workflows and analytics")