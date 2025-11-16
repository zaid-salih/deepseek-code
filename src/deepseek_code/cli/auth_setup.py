# deepseek-code/src/deepseek_code/cli/auth_setup.py
import os
import uuid
from typing import List, Dict
from deepseek_code.cli.terminal_ui import TerminalUI
from deepseek_code.core.team_manager import TeamManager

def first_time_setup(ui: TerminalUI):
    """Interactive first-time setup wizard"""
    ui.display_welcome()
    ui.console.print("[bold yellow]🎯 First-Time Setup[/bold yellow]")
    ui.console.print("=" * 50)
    
    # API Key Configuration
    ui.console.print("\n[bold blue]Step 1: API Configuration[/bold blue]")
    api_key = ui.prompt_user_input("Enter your DeepSeek API key")
    
    if not api_key:
        ui.display_error("API key is required!")
        return
    
    # Team Configuration
    ui.console.print("\n[bold blue]Step 2: Team Configuration[/bold blue]")
    team_name = ui.prompt_user_input("Enter your team name")
    
    if not team_name:
        team_name = "MyDevTeam"
        ui.display_warning(f"Using default team name: {team_name}")
    
    # User Configuration (3 users)
    ui.console.print("\n[bold blue]Step 3: User Configuration[/bold blue]")
    ui.console.print("Configure 3 team members (first user will be admin)")
    
    users = []
    for i in range(3):
        ui.console.print(f"\n--- User {i+1} Configuration ---")
        username = ui.prompt_user_input(f"Enter username for user {i+1}")
        
        if not username:
            username = f"user{i+1}"
            ui.display_warning(f"Using default username: {username}")
        
        user_data = {
            "user_id": f"user_{uuid.uuid4().hex[:8]}",
            "username": username,
            "preferences": {
                "theme": "dark",
                "default_language": "python",
                "code_style": "pep8",
                "auto_save": True,
                "max_file_size": 10000
            }
        }
        users.append(user_data)
        
        if i == 0:
            ui.display_success(f"Admin user '{username}' configured")
        else:
            ui.display_success(f"Team member '{username}' configured")
    
    # Confirm setup
    ui.console.print("\n[bold blue]Step 4: Configuration Summary[/bold blue]")
    ui.console.print(f"Team Name: {team_name}")
    ui.console.print("Users:")
    for i, user in enumerate(users):
        role = "Admin" if i == 0 else "Member"
        ui.console.print(f"  {i+1}. {user['username']} ({role})")
    
    if ui.prompt_yes_no("\nProceed with this configuration?"):
        # Initialize team manager and save configuration
        team_manager = TeamManager()
        team_config = team_manager.setup_team(api_key, team_name, users)
        
        if team_config:
            ui.display_success("✅ Setup complete! Team configuration saved.")
            ui.display_success(f"Active user: {users[0]['username']} (Admin)")
            ui.console.print(f"\nConfiguration saved to: {team_manager.config_dir}")
            ui.console.print("\nYou can now use:")
            ui.console.print("  [bold]deepseek-code chat[/bold] - Start interactive session")
            ui.console.print("  [bold]deepseek-code analyze <file>[/bold] - Analyze specific file")
            ui.console.print("  [bold]deepseek-code team-info[/bold] - Show team information")
        else:
            ui.display_error("Failed to save team configuration!")
    else:
        ui.display_warning("Setup cancelled.")