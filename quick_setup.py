# deepseek-code/quick_setup.py
#!/usr/bin/env python3
"""Quick setup wizard for DeepSeek-Code"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("🚀 DeepSeek-Code Quick Setup")
    print("=" * 40)
    
    # Initialize configuration first
    from deepseek_code.cli.init_system import initialize_complete_system
    from deepseek_code.cli.terminal_ui import TerminalUI
    
    ui = TerminalUI()
    
    ui.console.print("[bold green]Step 1: Initializing system...[/bold green]")
    initialize_complete_system()
    
    ui.console.print("\n[bold green]Step 2: Team configuration...[/bold green]")
    from deepseek_code.cli.auth_setup import first_time_setup
    first_time_setup(ui)
    
    ui.console.print("\n[bold green]Step 3: Verification...[/bold green]")
    from deepseek_code.core.config_manager import ConfigManager
    config_manager = ConfigManager()
    
    config_info = config_manager.get_config_info()
    if config_info["team_config_exists"]:
        ui.display_success("✅ Setup completed successfully!")
        
        ui.console.print("\n[bold]Configuration Summary:[/bold]")
        ui.console.print(f"📁 Config directory: {config_info['config_dir']}")
        ui.console.print(f"👥 Team: {config_info['team_name']}")
        ui.console.print(f"👤 Users: {config_info['user_count']}")
        
        ui.console.print("\n🎯 You can now use:")
        ui.console.print("   deepseek-code chat")
        ui.console.print("   deepseek-code analyze <file>")
        ui.console.print("   deepseek-code team workflow-status")
    else:
        ui.display_error("❌ Setup failed. Please run 'deepseek-code setup' manually.")

if __name__ == "__main__":
    main()