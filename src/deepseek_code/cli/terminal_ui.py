# deepseek-code/src/deepseek_code/cli/terminal_ui.py
import os
import sys
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.tree import Tree
from rich.live import Live
from rich.layout import Layout
import logging

class TerminalUI:
    """Rich-based terminal user interface"""
    
    def __init__(self):
        self.console = Console()
        self.logger = logging.getLogger(__name__)
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """
# 🚀 DeepSeek-Code

**AI-Powered CLI IDE** with full project context awareness and team collaboration.

*• Interactive terminal chat interface*
*• Multi-file analysis and editing*  
*• Git integration & code review*
*• 3-user team management*
"""
        self.console.print(Markdown(welcome_text))
        self.console.print()
    
    def display_chat_message(self, role: str, content: str, language: str = None):
        """Display chat message with syntax highlighting"""
        if role == "user":
            self.console.print(Panel(
                content, 
                title="[bold blue]You[/bold blue]",
                title_align="left",
                border_style="blue"
            ))
        else:
            # Try to extract and highlight code blocks
            if "```" in content:
                parts = content.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # Regular text
                        self.console.print(Markdown(part))
                    else:  # Code block
                        # Extract language if specified
                        lines = part.split('\n', 1)
                        if len(lines) > 1 and lines[0].strip():
                            lang = lines[0].strip()
                            code_content = lines[1]
                        else:
                            lang = language or "text"
                            code_content = part
                        
                        self.console.print(Syntax(
                            code_content, 
                            lang, 
                            theme="monokai",
                            line_numbers=True,
                            word_wrap=True
                        ))
            else:
                self.console.print(Panel(
                    Markdown(content),
                    title="[bold green]DeepSeek[/bold green]",
                    title_align="left", 
                    border_style="green"
                ))
    
    def display_file_tree(self, file_tree: Dict, title: str = "Project Structure"):
        """Display file tree structure"""
        tree = Tree(f"[bold blue]{title}[/bold blue]")
        
        def add_nodes(node, parent_tree):
            if node["type"] == "directory":
                branch = parent_tree.add(f"[yellow]📁 {node['name']}[/yellow]")
                for child in node.get("children", []):
                    add_nodes(child, branch)
            else:
                parent_tree.add(f"[white]📄 {node['name']}[/white]")
        
        add_nodes(file_tree, tree)
        self.console.print(tree)
    
    def display_project_info(self, project_info: Dict):
        """Display project information"""
        table = Table(title="📊 Project Overview")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Root Path", project_info["root"])
        table.add_row("Total Files", str(len(project_info["files"])))
        table.add_row("Total Size", f"{project_info['total_size'] / 1024 / 1024:.2f} MB")
        table.add_row("File Types", ", ".join([
            f"{ext}: {count}" for ext, count in project_info["file_types"].items()
        ][:5]))  # Show top 5 file types
        
        self.console.print(table)
    
    def prompt_user_input(self, message: str = "Ask DeepSeek:") -> str:
        """Get user input with rich prompt"""
        return Prompt.ask(f"[bold blue]{message}[/bold blue]")
    
    def prompt_yes_no(self, message: str) -> bool:
        """Get yes/no confirmation"""
        return Confirm.ask(f"[yellow]{message}[/yellow]")
    
    def display_loading(self, message: str = "Processing..."):
        """Display loading animation"""
        with self.console.status(f"[bold green]{message}[/bold green]") as status:
            yield
    
    def display_error(self, message: str):
        """Display error message"""
        self.console.print(f"[bold red]Error: {message}[/bold red]")
    
    def display_success(self, message: str):
        """Display success message"""
        self.console.print(f"[bold green]✅ {message}[/bold green]")
    
    def display_warning(self, message: str):
        """Display warning message"""
        self.console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")
    
    def display_team_info(self, team_config: Dict, active_user: Dict):
        """Display team information"""
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
        
        self.console.print(table)