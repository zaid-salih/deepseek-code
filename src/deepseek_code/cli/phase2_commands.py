# deepseek-code/src/deepseek_code/cli/phase2_commands.py
import typer
from typing import Optional, List
from pathlib import Path
import json

from .terminal_ui import TerminalUI
from ..core.git_integration import GitIntegration
from ..core.refactoring_engine import RefactoringEngine
from ..core.testing_integration import TestingIntegration
from typing import Dict, List, Optional, Any
from typing import Dict, List, Optional, Any
from ..core.config_manager import ConfigManager
from ..core.file_manager import FileManager
from ..core.ai_engine import DeepSeekAI
from ..core.team_manager import TeamManager

# Create Phase 2 Typer app
phase2_app = typer.Typer(
    name="phase2",
    help="🚀 Phase 2: Advanced Code Operations",
    rich_markup_mode="rich"
)

ui = TerminalUI()

@phase2_app.command()
def git_status():
    """Show git status with detailed information"""
    git = GitIntegration()
    
    if not git.is_git_repository():
        ui.display_error("Not a git repository")
        return
    
    status = git.get_status()
    
    if "error" in status:
        ui.display_error(f"Git status failed: {status['error']}")
        return
    
    # Display status in a nice table
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

@phase2_app.command()
def git_branches():
    """Show all git branches"""
    git = GitIntegration()
    
    if not git.is_git_repository():
        ui.display_error("Not a git repository")
        return
    
    branches = git.get_branches()
    
    if "error" in branches:
        ui.display_error(f"Git branches failed: {branches['error']}")
        return
    
    from rich.table import Table
    
    table = Table(title="Git Branches")
    table.add_column("Branch", style="cyan")
    table.add_column("Current", style="green")
    table.add_column("Commit", style="yellow")
    table.add_column("Upstream", style="white")
    
    for branch in branches['branches']:
        current = "✅" if branch['current'] else ""
        table.add_row(
            branch['name'],
            current,
            branch.get('commit', ''),
            branch.get('upstream', '')
        )
    
    ui.console.print(table)

@phase2_app.command()
def git_commit(
    message: str = typer.Option(..., "--message", "-m", help="Commit message"),
    files: List[str] = typer.Option(None, "--file", "-f", help="Specific files to commit")
):
    """Commit changes with message"""
    git = GitIntegration()
    
    if not git.is_git_repository():
        ui.display_error("Not a git repository")
        return
    
    status = git.get_status()
    if not status.get('has_changes'):
        ui.display_warning("No changes to commit")
        return
    
    result = git.commit(message, files)
    
    if result['success']:
        ui.display_success(f"Committed: {message}")
    else:
        ui.display_error(f"Commit failed: {result.get('message', 'Unknown error')}")

@phase2_app.command()
def analyze_dependencies(
    file_path: str = typer.Argument(..., help="File to analyze"),
    visualize: bool = typer.Option(False, "--visualize", "-v", help="Generate visualization")
):
    """Analyze code dependencies"""
    file_manager = FileManager()
    refactoring_engine = RefactoringEngine(file_manager, None)  # AI not needed for analysis
    
    analysis = refactoring_engine.analyze_dependencies(file_path)
    
    if "error" in analysis:
        ui.display_error(analysis["error"])
        return
    
    ui.console.print(f"\n[bold blue]Dependency Analysis for {file_path}[/bold blue]")
    ui.console.print(f"Language: {analysis.get('language', 'unknown')}")
    
    if 'imports' in analysis and analysis['imports']:
        ui.console.print("\n[bold]Imports:[/bold]")
        for imp in analysis['imports']:
            ui.console.print(f"  - {imp}")
    
    if 'functions' in analysis and analysis['functions']:
        ui.console.print(f"\n[bold]Functions ({len(analysis['functions'])}):[/bold]")
        ui.console.print("  " + ", ".join(analysis['functions']))
    
    if 'classes' in analysis and analysis['classes']:
        ui.console.print(f"\n[bold]Classes ({len(analysis['classes'])}):[/bold]")
        ui.console.print("  " + ", ".join(analysis['classes']))
    
    if visualize:
        ui.console.print("\n[bold]Generating dependency visualization...[/bold]")
        visualization = refactoring_engine.visualize_dependencies()
        ui.console.print(f"Nodes: {len(visualization['nodes'])}")
        ui.console.print(f"Edges: {len(visualization['edges'])}")

@phase2_app.command()
def test_discover():
    """Discover testing frameworks in project"""
    testing = TestingIntegration()
    frameworks = testing.detect_testing_frameworks()
    
    if not frameworks:
        ui.display_warning("No testing frameworks detected")
        return
    
    from rich.table import Table
    
    table = Table(title="Detected Testing Frameworks")
    table.add_column("Framework", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")
    
    for framework, config in frameworks.items():
        status = "✅ Detected" if config.get('detected') else "❌ Not detected"
        details = f"Files: {config.get('test_file_count', 0)}" if config.get('test_file_count') else "Config found"
        
        table.add_row(framework, status, details)
    
    ui.console.print(table)

@phase2_app.command()
def test_run(
    framework: str = typer.Option("auto", "--framework", "-f", help="Testing framework"),
    test_path: str = typer.Option(None, "--test-path", "-t", help="Specific test to run")
):
    """Run tests using detected framework"""
    testing = TestingIntegration()
    
    with ui.console.status("[bold green]Running tests...[/bold green]"):
        result = testing.run_tests(framework, test_path)
    
    if "error" in result:
        ui.display_error(result["error"])
        return
    
    if result["success"]:
        ui.display_success(f"Tests passed using {result['framework']}!")
        if result.get("stdout"):
            ui.console.print("\n[bold]Test Output:[/bold]")
            ui.console.print(result["stdout"])
    else:
        ui.display_error(f"Tests failed using {result['framework']}!")
        if result.get("stderr"):
            ui.console.print("\n[bold]Error Output:[/bold]")
            ui.console.print(result["stderr"])

@phase2_app.command()
def config_info():
    """Show configuration information"""
    config_manager = ConfigManager()
    info = config_manager.get_config_info()
    
    from rich.table import Table
    
    table = Table(title="Configuration Information")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Config Directory", info["config_dir"])
    table.add_row("Team Config", "✅ Exists" if info["team_config_exists"] else "❌ Missing")
    table.add_row("Usage Log", "✅ Exists" if info["usage_log_exists"] else "❌ Missing")
    table.add_row("User Preference Files", str(info["user_preference_files"]))
    table.add_row("Team Name", info["team_name"])
    table.add_row("User Count", str(info["user_count"]))
    table.add_row("Total Backups", str(info["total_backups"]))
    
    ui.console.print(table)

@phase2_app.command()
def refactor(
    files: List[str] = typer.Argument(..., help="Files to refactor"),
    instructions: str = typer.Option(..., "--instructions", "-i", help="Refactoring instructions"),
    language: str = typer.Option(None, "--language", "-l", help="Programming language")
):
    """Refactor code across multiple files"""
    # Load team config for AI access
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        ui.display_error("Team configuration not found. Please run setup first.")
        return
    
    api_key = team_manager.decrypt_api_key(team_config["api_key"])
    ai_engine = DeepSeekAI(api_key)
    file_manager = FileManager()
    refactoring_engine = RefactoringEngine(file_manager, ai_engine)
    
    with ui.console.status("[bold green]Refactoring code...[/bold green]"):
        result = refactoring_engine.refactor_code(files, instructions, language)
    
    if "error" in result:
        ui.display_error(result["error"])
        if "backup_id" in result:
            ui.display_info(f"Backup ID: {result['backup_id']} (use for rollback)")
        return
    
    ui.display_success(f"Refactoring completed successfully!")
    ui.console.print(f"Files modified: {result['files_modified']}")
    ui.console.print(f"Backup ID: {result['backup_id']}")