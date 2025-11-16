# deepseek-code/src/deepseek_code/cli/init_system.py
#!/usr/bin/env python3
"""Complete system initialization for DeepSeek-Code"""

import os
import sys
import json
import shutil
from pathlib import Path
from cryptography.fernet import Fernet

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from deepseek_code.core.config_manager import ConfigManager
from deepseek_code.core.team_manager import TeamManager
from deepseek_code.cli.terminal_ui import TerminalUI

def initialize_complete_system():
    """Initialize the complete DeepSeek-Code system"""
    ui = TerminalUI()
    
    ui.console.print("[bold blue]🎯 DeepSeek-Code System Initialization[/bold blue]")
    ui.console.print("=" * 60)
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    team_manager = TeamManager()
    
    # Create all necessary directories
    directories = [
        config_manager.config_dir,
        config_manager.backup_dir,
        Path("~/.deepseek-code/refactoring_backups").expanduser(),
        Path("~/.deepseek-code/templates").expanduser(),
        Path("~/.deepseek-code/code_reviews").expanduser()
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        ui.console.print(f"📁 Created: {directory}")
    
    # Initialize configuration structure
    if config_manager.initialize_config_structure():
        ui.display_success("Configuration structure initialized!")
    else:
        ui.display_error("Failed to initialize configuration structure")
        return False
    
    # Create example configuration files if they don't exist
    create_example_configs(config_manager, ui)
    
    # Display system information
    display_system_info(config_manager, ui)
    
    ui.console.print("\n[bold green]✅ System initialization complete![/bold green]")
    ui.console.print("\n[bold]Next steps:[/bold]")
    ui.console.print("1. Run [bold]deepseek-code setup[/bold] to configure your team and API key")
    ui.console.print("2. Run [bold]deepseek-code team workflow-status[/bold] to check team workflows")
    ui.console.print("3. Run [bold]deepseek-code team analytics[/bold] to view usage analytics")
    
    return True

def create_example_configs(config_manager: ConfigManager, ui: TerminalUI):
    """Create example configuration files"""
    
    # Example team configuration
    example_team_config = {
        "team_name": "Example Development Team",
        "team_id": "team_example_123",
        "api_key": "encrypted_example_key_placeholder",
        "created_date": "2024-01-01T00:00:00Z",
        "active_user": "user_admin_001",
        "users": [
            {
                "user_id": "user_admin_001",
                "username": "team_lead",
                "role": "admin",
                "preferences": {
                    "theme": "dark",
                    "default_language": "python",
                    "code_style": "pep8",
                    "auto_save": True,
                    "max_file_size": 10000
                },
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-15T10:30:00Z"
            },
            {
                "user_id": "user_dev_002",
                "username": "senior_dev",
                "role": "member",
                "preferences": {
                    "theme": "light",
                    "default_language": "javascript",
                    "code_style": "standard",
                    "auto_save": False,
                    "max_file_size": 5000
                },
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-14T15:45:00Z"
            },
            {
                "user_id": "user_dev_003", 
                "username": "junior_dev",
                "role": "member",
                "preferences": {
                    "theme": "dark",
                    "default_language": "python",
                    "code_style": "pep8",
                    "auto_save": True,
                    "max_file_size": 8000
                },
                "created_at": "2024-01-01T00:00:00Z",
                "last_active": "2024-01-13T09:15:00Z"
            }
        ]
    }
    
    # Example usage log
    example_usage_log = {
        "2024-01-15": {
            "user_admin_001": {
                "tokens_used": 1250,
                "operations": {
                    "chat_completion": 5,
                    "code_analysis": 3,
                    "refactoring": 1
                }
            },
            "user_dev_002": {
                "tokens_used": 850,
                "operations": {
                    "chat_completion": 3,
                    "code_analysis": 2
                }
            }
        },
        "2024-01-14": {
            "user_admin_001": {
                "tokens_used": 980,
                "operations": {
                    "chat_completion": 4,
                    "refactoring": 2
                }
            },
            "user_dev_003": {
                "tokens_used": 420,
                "operations": {
                    "chat_completion": 2
                }
            }
        }
    }
    
    # Create example files only if they don't exist
    if not config_manager.team_config_path.exists():
        config_manager.save_team_config(example_team_config)
        ui.console.print("📄 Created: example team_config.json")
    
    if not config_manager.usage_log_path.exists():
        config_manager.save_usage_log(example_usage_log)
        ui.console.print("📊 Created: example usage_log.json")
    
    # Create example user preference files
    for user in example_team_config["users"]:
        user_id = user["user_id"]
        pref_file = config_manager.config_dir / f"user_preferences_{user_id}.json"
        if not pref_file.exists():
            config_manager.save_user_preferences(user_id, user["preferences"])
            ui.console.print(f"👤 Created: user_preferences_{user_id}.json")

def display_system_info(config_manager: ConfigManager, ui: TerminalUI):
    """Display system configuration information"""
    from rich.table import Table
    from rich.panel import Panel
    
    info = config_manager.get_config_info()
    
    table = Table(show_header=False, show_edge=False, box=None)
    table.add_column("Category", style="cyan")
    table.add_column("Status", style="white")
    
    table.add_row("Config Directory", info["config_dir"])
    table.add_row("Team Configuration", "✅ Ready" if info["team_config_exists"] else "❌ Missing")
    table.add_row("Usage Tracking", "✅ Ready" if info["usage_log_exists"] else "❌ Missing")
    table.add_row("User Profiles", f"👥 {info['user_preference_files']} configured")
    table.add_row("Backup System", f"💾 {info['total_backups']} backups")
    
    ui.console.print(Panel(table, title="System Configuration Status", border_style="green"))
    
    # Show directory structure
    ui.console.print("\n[bold]📁 Configuration Directory Structure:[/bold]")
    config_tree = generate_config_tree(config_manager.config_dir)
    ui.console.print(config_tree)

def generate_config_tree(config_dir: Path, max_depth: int = 2) -> str:
    """Generate a tree representation of the configuration directory"""
    def build_tree(path: Path, prefix: str = "", depth: int = 0) -> str:
        if depth > max_depth:
            return ""
        
        name = path.name if path != config_dir else "~/.deepseek-code"
        result = prefix + "📁 " + name + "\n"
        
        if path.is_dir():
            children = sorted(path.iterdir())
            for i, child in enumerate(children):
                if child.name.startswith('.'):
                    continue
                    
                is_last = i == len(children) - 1
                child_prefix = prefix + ("    " if is_last else "│   ")
                connector = "└── " if is_last else "├── "
                
                if child.is_dir():
                    result += prefix + connector + build_tree(child, child_prefix, depth + 1).lstrip()
                else:
                    result += prefix + connector + "📄 " + child.name + "\n"
        
        return result
    
    return build_tree(config_dir).rstrip()

if __name__ == "__main__":
    initialize_complete_system()