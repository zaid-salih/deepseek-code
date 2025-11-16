#!/usr/bin/env python3
"""DeepSeek-Code CLI - Improved Chat Version"""

import os
import sys
import typer
from typing import Optional, List, Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from deepseek_code.core.ai_engine import DeepSeekAI
from deepseek_code.core.team_manager import TeamManager
from deepseek_code.core.file_manager import FileManager
from deepseek_code.core.config_manager import ConfigManager
from deepseek_code.cli.terminal_ui import TerminalUI

app = typer.Typer(
    name="deepseek-code",
    help="🚀 AI-Powered CLI IDE with DeepSeek integration",
    rich_markup_mode="rich"
)

ui = TerminalUI()

@app.command()
def chat():
    """Start interactive chat session with improved streaming"""
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        ui.display_error("Team configuration not found. Please run setup first.")
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
            
            # Display AI response with improved streaming
            ui.console.print()
            ui.console.print("[bold green]🤖 DeepSeek:[/bold green]")
            
            response_text = ""
            try:
                # Collect all chunks first, then display
                with ui.console.status("[bold green]Thinking...[/bold green]"):
                    chunks = []
                    for chunk in ai_engine.chat_completion(
                        conversation_history[-10:],
                        stream=True
                    ):
                        chunks.append(chunk)
                
                # Display the complete response
                response_text = "".join(chunks)
                ui.console.print(response_text)
                ui.console.print()
                
            except Exception as e:
                ui.display_error(f"AI request failed: {e}")
                continue
            
            # Add AI response to history
            conversation_history.append({
                "role": "assistant", 
                "content": response_text
            })
            
        except KeyboardInterrupt:
            ui.console.print("\n[yellow]Session interrupted. Use 'quit' to exit properly.[/yellow]")
            break
        except Exception as e:
            ui.display_error(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    app()
