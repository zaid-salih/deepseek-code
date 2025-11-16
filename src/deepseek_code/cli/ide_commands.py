# deepseek-code/src/deepseek_code/cli/ide_commands.py
import typer
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .terminal_ui import TerminalUI

ide_app = typer.Typer(
    name="ide",
    help="🚀 IDE Integration Commands",
    rich_markup_mode="rich"
)

ui = TerminalUI()

@ide_app.command()
def vscode_install():
    """Install VS Code extension (development mode)"""
    vscode_dir = Path("vscode_extension")
    
    if not vscode_dir.exists():
        ui.display_error("VS Code extension directory not found. Make sure you're in the project root.")
        return
    
    try:
        # Check if VS Code CLI is available
        result = subprocess.run(["code", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            ui.display_error("VS Code CLI not found. Please install VS Code and ensure 'code' command is in PATH.")
            return
        
        # Install the extension
        ui.console.print("[bold green]Installing VS Code extension...[/bold green]")
        subprocess.run(["code", "--install-extension", str(vscode_dir)], check=True)
        ui.display_success("VS Code extension installed successfully!")
        
    except subprocess.CalledProcessError as e:
        ui.display_error(f"Failed to install VS Code extension: {e}")
    except Exception as e:
        ui.display_error(f"Unexpected error: {e}")

@ide_app.command()
def vscode_package():
    """Package VS Code extension for distribution"""
    vscode_dir = Path("vscode_extension")
    
    if not vscode_dir.exists():
        ui.display_error("VS Code extension directory not found.")
        return
    
    try:
        # Check if vsce is available
        result = subprocess.run(["vsce", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            ui.display_error("VS Code Extension Manager (vsce) not found. Install with: npm install -g vsce")
            return
        
        # Package the extension
        ui.console.print("[bold green]Packaging VS Code extension...[/bold green]")
        subprocess.run(["vsce", "package"], cwd=vscode_dir, check=True)
        ui.display_success("VS Code extension packaged successfully!")
        
    except subprocess.CalledProcessError as e:
        ui.display_error(f"Failed to package VS Code extension: {e}")
    except Exception as e:
        ui.display_error(f"Unexpected error: {e}")

@ide_app.command()
def vs_build():
    """Build Visual Studio extension"""
    vs_dir = Path("visualstudio_extension")
    
    if not vs_dir.exists():
        ui.display_error("Visual Studio extension directory not found.")
        return
    
    try:
        # This would use MSBuild - simplified for now
        ui.console.print("[bold green]Visual Studio extension build would run here...[/bold green]")
        ui.display_warning("Visual Studio extension building requires MSBuild and Visual Studio SDK.")
        
    except Exception as e:
        ui.display_error(f"Unexpected error: {e}")

@ide_app.command()
def lsp_start():
    """Start Language Server Protocol server"""
    try:
        from ..ide.lsp_server import start_lsp_server
        ui.console.print("[bold green]Starting DeepSeek-Code LSP server...[/bold green]")
        ui.console.print("LSP server running on stdio...")
        start_lsp_server()
    except ImportError as e:
        ui.display_error(f"LSP server dependencies missing: {e}")
        ui.console.print("Install LSP dependencies: pip install pygls lsprotocol")
    except Exception as e:
        ui.display_error(f"Failed to start LSP server: {e}")

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
        from ..ide.lsp_server import DeepSeekLanguageServer
        table.add_row("LSP Server", "✅ Available", "Python implementation ready")
    except ImportError:
        table.add_row("LSP Server", "⚠️ Dependencies Missing", "Install pygls and lsprotocol")
    except Exception as e:
        table.add_row("LSP Server", "❌ Error", str(e))
    
    ui.console.print(table)
    
    ui.console.print("\n[bold]Next steps:[/bold]")
    ui.console.print("1. For VS Code: Run [bold]deepseek-code ide vscode-install[/bold]")
    ui.console.print("2. For LSP: Run [bold]deepseek-code ide lsp-start[/bold] in LSP mode")