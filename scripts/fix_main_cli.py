# deepseek-code/fix_main_cli.py
#!/usr/bin/env python3
"""Fix the main CLI by updating phase commands"""

import os
import sys
from pathlib import Path

def fix_phase2_commands():
    """Fix imports in phase2_commands.py"""
    file_path = Path("src/deepseek_code/cli/phase2_commands.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the import for TestingIntegration
    if "from ..core.testing_integration import TestingIntegration" in content:
        # Add the missing import
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith("from ..core.testing_integration import TestingIntegration"):
                # Add the import after this line
                lines.insert(i + 1, "from typing import Dict, List, Optional, Any")
                break
        
        content = '\n'.join(lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed phase2_commands.py")
        return True
    
    return False

def fix_phase4_commands():
    """Fix imports in phase4_commands.py"""
    file_path = Path("src/deepseek_code/cli/phase4_commands.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add missing imports
    if "from typing import Optional, List" in content:
        # Replace with more comprehensive imports
        content = content.replace(
            "from typing import Optional, List",
            "from typing import Optional, List, Dict, Any"
        )
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed phase4_commands.py")
        return True
    
    return False

def fix_main_cli():
    """Fix the main CLI file"""
    file_path = Path("src/deepseek_code/cli/main.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Clear the cache imports at the top
    if "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))" in content:
        # This is already there, just need to fix phase commands
        print("✅ main.py structure is good")
        return True
    
    return False

def create_working_main():
    """Create a working version of main.py that imports only working modules"""
    working_main = '''#!/usr/bin/env python3
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
    
    api_key = team_manager.decrypt_api_key(team_config["api_key"])
    ai_engine = DeepSeekAI(api_key)
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
    
    ui.display_success("Ready for questions! Type 'quit' to exit.")
    
    while True:
        try:
            user_input = ui.prompt_user_input()
            
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
    ui.display_team_info(team_config, active_user)

if __name__ == "__main__":
    app()
'''

    with open("src/deepseek_code/cli/working_main.py", 'w', encoding='utf-8') as f:
        f.write(working_main)
    
    print("✅ Created working_main.py with core functionality")
    return True

def main():
    print("🔧 Fixing Main CLI")
    print("=" * 40)
    
    # Fix phase commands
    fix_phase2_commands()
    fix_phase4_commands()
    
    # Create working main
    create_working_main()
    
    print("\n🚀 Created working CLI versions:")
    print("  python -m deepseek_code.cli.simple_main --help (Basic)")
    print("  python -m deepseek_code.cli.working_main --help (Advanced)")
    
    return True

if __name__ == "__main__":
    main()