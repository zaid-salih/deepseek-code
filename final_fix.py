# deepseek-code/final_fix.py
#!/usr/bin/env python3
"""Final fix for the main CLI import issues"""

import os
import sys
from pathlib import Path

def fix_testing_integration_imports():
    """Fix the Any import in testing_integration.py"""
    file_path = Path("src/deepseek_code/core/testing_integration.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add the missing Any import
    if "from typing import" in content:
        if "Any" not in content.split("from typing import")[1].split("\n")[0]:
            content = content.replace(
                "from typing import Dict, List, Optional",
                "from typing import Dict, List, Optional, Any"
            )
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Fixed testing_integration.py imports")
            return True
    return False

def create_final_working_main():
    """Create a final working main that includes all features"""
    final_main = '''#!/usr/bin/env python3
"""DeepSeek-Code CLI - Final Working Version with All Features"""

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
from deepseek_code.core.git_integration import GitIntegration
from deepseek_code.core.project_templates import ProjectTemplateManager
from deepseek_code.cli.terminal_ui import TerminalUI
from deepseek_code.cli.auth_setup import first_time_setup

app = typer.Typer(
    name="deepseek-code",
    help="🚀 AI-Powered CLI IDE with DeepSeek integration",
    rich_markup_mode="rich"
)

# Create sub-apps for different feature groups
team_app = typer.Typer(help="Team workflows and collaboration")
app.add_typer(team_app, name="team")

ide_app = typer.Typer(help="IDE integration commands")
app.add_typer(ide_app, name="ide")

ui = TerminalUI()

# Basic Commands
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
                        conversation_history[-10:],
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
            ui.console.print("\\n[yellow]Session interrupted. Use 'quit' to exit properly.[/yellow]")
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

# Team Commands
@team_app.command()
def info():
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

@team_app.command()
def workflow_status():
    """Show team workflow status"""
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        ui.display_error("Team configuration not found. Please run 'deepseek-code setup' first.")
        return
    
    from rich.table import Table
    
    # Team information
    team_table = Table(title="👥 Team Information")
    team_table.add_column("User", style="cyan")
    team_table.add_column("Role", style="white")
    team_table.add_column("Last Active", style="yellow")
    team_table.add_column("Status", style="green")
    
    active_user = team_manager.get_active_user()
    for user in team_config["users"]:
        role = user["role"]
        if user["user_id"] == active_user["user_id"]:
            role = f"🟢 {role}"
        
        team_table.add_row(
            user["username"],
            role,
            user.get("last_active", "Unknown").split('T')[0],
            "🟢 Active" if user["user_id"] == active_user["user_id"] else "⚪ Inactive"
        )
    
    ui.console.print(team_table)

@team_app.command()
def template_list():
    """List available project templates"""
    template_manager = ProjectTemplateManager()
    templates = template_manager.list_templates()
    
    if not templates:
        ui.display_warning("No templates found.")
        return
    
    from rich.table import Table
    
    table = Table(title="📁 Project Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Files", style="yellow")
    table.add_column("Created By", style="green")
    
    for template in templates:
        table.add_row(
            template["name"],
            template.get("description", "No description"),
            str(len(template.get("files", []))),
            template.get("created_by", "Unknown")
        )
    
    ui.console.print(table)

# Git Commands
@app.command()
def git_status():
    """Show git status"""
    git = GitIntegration()
    
    if not git.is_git_repository():
        ui.display_error("Not a git repository")
        return
    
    status = git.get_status()
    
    if "error" in status:
        ui.display_error(f"Git status failed: {status['error']}")
        return
    
    from rich.table import Table
    
    table = Table(title=f"Git Status - {status['current_branch']}")
    table.add_column("Status", style="cyan")
    table.add_column("File", style="white")
    table.add_column("Type", style="yellow")
    
    for file in status['files']:
        table.add_row(file['status'], file['path'], file['type'])
    
    ui.console.print(table)
    
    if not status['has_changes']:
        ui.display_success("Working directory clean")

# IDE Commands
@ide_app.command()
def status():
    """Show IDE integration status"""
    from rich.table import Table
    
    table = Table(title="IDE Integration Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="yellow")
    
    # VS Code Extension
    vscode_dir = Path("vscode_extension")
    if vscode_dir.exists():
        package_json = vscode_dir / "package.json"
        if package_json.exists():
            table.add_row("VS Code Extension", "✅ Available", "Ready for development")
        else:
            table.add_row("VS Code Extension", "⚠️ Incomplete", "package.json missing")
    else:
        table.add_row("VS Code Extension", "❌ Missing", "Directory not found")
    
    # Visual Studio Extension
    vs_dir = Path("visualstudio_extension")
    if vs_dir.exists():
        csproj_files = list(vs_dir.glob("*.csproj"))
        if csproj_files:
            table.add_row("Visual Studio Extension", "✅ Available", "Ready for development")
        else:
            table.add_row("Visual Studio Extension", "⚠️ Incomplete", "Project file missing")
    else:
        table.add_row("Visual Studio Extension", "❌ Missing", "Directory not found")
    
    # LSP Server
    try:
        from deepseek_code.ide.lsp_server import DeepSeekLanguageServer
        table.add_row("LSP Server", "✅ Available", "Python implementation ready")
    except ImportError:
        table.add_row("LSP Server", "⚠️ Dependencies Missing", "Install pygls and lsprotocol")
    except Exception as e:
        table.add_row("LSP Server", "❌ Error", str(e))
    
    ui.console.print(table)

if __name__ == "__main__":
    app()
'''
    
    with open("src/deepseek_code/cli/final_main.py", 'w', encoding='utf-8') as f:
        f.write(final_main)
    
    print("✅ Created final_main.py with all features")
    return True

def update_package_entry_points():
    """Update the package entry points to use the final main"""
    # This would update pyproject.toml to use final_main instead of main
    print("💡 To use the final version, run: python -m deepseek_code.cli.final_main")
    return True

def main():
    print("🔧 Final DeepSeek-Code Fix")
    print("=" * 40)
    
    # Fix the testing integration imports
    fix_testing_integration_imports()
    
    # Create the final working main with all features
    create_final_working_main()
    
    print("\n🎉 Final fixes applied!")
    print("\n🚀 You can now use:")
    print("  python -m deepseek_code.cli.final_main --help")
    print("  python -m deepseek_code.cli.final_main chat")
    print("  python -m deepseek_code.cli.final_main team info")
    print("  python -m deepseek_code.cli.final_main team template-list")
    print("  python -m deepseek_code.cli.final_main git-status")
    
    return True

if __name__ == "__main__":
    main()