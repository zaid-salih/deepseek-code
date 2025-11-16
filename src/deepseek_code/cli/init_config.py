# deepseek-code/src/deepseek_code/cli/init_config.py
#!/usr/bin/env python3
"""Initialize configuration structure"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from deepseek_code.core.config_manager import ConfigManager
from deepseek_code.cli.terminal_ui import TerminalUI

def initialize_configuration():
    """Initialize the configuration structure"""
    ui = TerminalUI()
    config_manager = ConfigManager()
    
    ui.console.print("[bold blue]🎯 Initializing DeepSeek-Code Configuration[/bold blue]")
    ui.console.print("=" * 50)
    
    if config_manager.initialize_config_structure():
        info = config_manager.get_config_info()
        
        ui.display_success("Configuration structure initialized successfully!")
        
        from rich.table import Table
        table = Table(show_header=False, show_edge=False)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Config Directory", info["config_dir"])
        table.add_row("Team Config", "✅ Created" if info["team_config_exists"] else "❌ Failed")
        table.add_row("Usage Log", "✅ Created" if info["usage_log_exists"] else "❌ Failed")
        table.add_row("User Preferences", f"✅ {info['user_preference_files']} files")
        
        ui.console.print(table)
        
        ui.console.print("\n[bold]Next steps:[/bold]")
        ui.console.print("1. Run [bold]deepseek-code setup[/bold] to configure your team")
        ui.console.print("2. Run [bold]deepseek-code advanced config-info[/bold] to verify configuration")
        
    else:
        ui.display_error("Failed to initialize configuration structure")

if __name__ == "__main__":
    initialize_configuration()