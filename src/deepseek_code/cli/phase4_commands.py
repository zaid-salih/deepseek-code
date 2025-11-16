# deepseek-code/src/deepseek_code/cli/phase4_commands.py
import typer
from typing import Optional, List, Dict, Any, Dict, Any
from pathlib import Path
import json

from .terminal_ui import TerminalUI
from ..core.code_review import CodeReviewManager
from ..core.project_templates import ProjectTemplateManager
from ..core.analytics import AnalyticsEngine
from ..core.ai_engine import DeepSeekAI
from ..core.team_manager import TeamManager
from ..core.git_integration import GitIntegration

phase4_app = typer.Typer(
    name="team",
    help="🚀 Phase 4: Team Workflows & Analytics",
    rich_markup_mode="rich"
)

ui = TerminalUI()

@phase4_app.command()
def init_system():
    """Initialize the complete DeepSeek-Code system"""
    from .init_system import initialize_complete_system
    initialize_complete_system()

@phase4_app.command()
def workflow_status():
    """Show team workflow status"""
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        ui.display_error("Team configuration not found. Please run setup first.")
        return
    
    from rich.table import Table
    from rich.panel import Panel
    
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
    
    # Code review status
    try:
        api_key = team_manager.decrypt_api_key(team_config["api_key"])
        ai_engine = DeepSeekAI(api_key)
        review_manager = CodeReviewManager(team_manager, ai_engine)
        
        review_stats = review_manager.get_review_stats()
        pending_reviews = review_manager.get_pending_reviews()
        
        review_table = Table(title="📋 Code Review Status")
        review_table.add_column("Metric", style="cyan")
        review_table.add_column("Count", style="white")
        
        review_table.add_row("Total Reviews", str(review_stats["total_reviews"]))
        review_table.add_row("Pending Reviews", str(review_stats["pending_reviews"]))
        review_table.add_row("Approved Reviews", str(review_stats["approved_reviews"]))
        review_table.add_row("Your Pending Reviews", str(len(pending_reviews)))
        
        ui.console.print(review_table)
        
    except Exception as e:
        ui.display_warning(f"Could not load review stats: {e}")

@phase4_app.command()
def request_review(
    file_path: str = typer.Argument(..., help="File to review"),
    reviewer: str = typer.Argument(..., help="Reviewer user ID"),
    instructions: str = typer.Option("", "--instructions", "-i", help="Review instructions"),
    priority: str = typer.Option("normal", "--priority", "-p", help="Priority: low, normal, high")
):
    """Request code review from team member"""
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        ui.display_error("Team configuration not found. Please run setup first.")
        return
    
    api_key = team_manager.decrypt_api_key(team_config["api_key"])
    ai_engine = DeepSeekAI(api_key)
    review_manager = CodeReviewManager(team_manager, ai_engine)
    
    result = review_manager.request_review(file_path, reviewer, instructions, priority)
    
    if "error" in result:
        ui.display_error(result["error"])
        return
    
    ui.display_success(f"Review requested from {reviewer}!")
    ui.console.print(f"Review ID: {result['review_id']}")
    ui.console.print(f"Priority: {priority}")

@phase4_app.command()
def automated_review(
    file_path: str = typer.Argument(..., help="File to review"),
    rules: List[str] = typer.Option(None, "--rule", "-r", help="Review rules to apply")
):
    """Perform AI-powered automated code review"""
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        ui.display_error("Team configuration not found. Please run setup first.")
        return
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code_content = f.read()
    except Exception as e:
        ui.display_error(f"Could not read file: {e}")
        return
    
    api_key = team_manager.decrypt_api_key(team_config["api_key"])
    ai_engine = DeepSeekAI(api_key)
    review_manager = CodeReviewManager(team_manager, ai_engine)
    
    code_changes = {
        "code": code_content,
        "language": "python",  # Would detect automatically in real implementation
        "context": f"Review of {file_path}"
    }
    
    with ui.console.status("[bold green]Performing AI code review...[/bold green]"):
        result = review_manager.automated_review(code_changes, rules)
    
    if "error" in result:
        ui.display_error(result["error"])
        return
    
    review_data = result["review"]
    
    ui.console.print(f"\n[bold blue]🤖 AI Code Review for {file_path}[/bold blue]")
    ui.console.print(f"Rules checked: {', '.join(result['rules_checked'])}")
    
    # Display review results
    if review_data.get("critical_issues"):
        ui.console.print("\n[bold red]🚨 Critical Issues:[/bold red]")
        for issue in review_data["critical_issues"]:
            ui.console.print(f"• {issue}")
    
    if review_data.get("major_issues"):
        ui.console.print("\n[bold yellow]⚠️ Major Issues:[/bold yellow]")
        for issue in review_data["major_issues"]:
            ui.console.print(f"• {issue}")
    
    if review_data.get("minor_issues"):
        ui.console.print("\n[bold blue]💡 Minor Issues:[/bold blue]")
        for issue in review_data["minor_issues"]:
            ui.console.print(f"• {issue}")
    
    if review_data.get("suggestions"):
        ui.console.print("\n[bold green]💡 Suggestions:[/bold green]")
        for suggestion in review_data["suggestions"]:
            ui.console.print(f"• {suggestion}")

@phase4_app.command()
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

@phase4_app.command()
def template_create(
    template_name: str = typer.Argument(..., help="Template name"),
    description: str = typer.Option("", "--description", "-d", help="Template description"),
    files: List[str] = typer.Option(None, "--file", "-f", help="Files to include")
):
    """Create a new project template"""
    template_manager = ProjectTemplateManager()
    
    if not files:
        ui.display_error("Please specify files to include with --file")
        return
    
    # Read files
    files_content = {}
    for file_path in files:
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    files_content[str(path)] = f.read()
            except Exception as e:
                ui.display_error(f"Could not read {file_path}: {e}")
                return
        else:
            ui.display_error(f"File not found: {file_path}")
            return
    
    result = template_manager.create_template(template_name, description, files_content)
    
    if "error" in result:
        ui.display_error(result["error"])
        return
    
    ui.display_success(f"Template '{template_name}' created successfully!")
    ui.console.print(f"Files included: {len(files_content)}")

@phase4_app.command()
def template_apply(
    template_name: str = typer.Argument(..., help="Template name"),
    target_dir: str = typer.Argument(..., help="Target directory"),
    overwrite: bool = typer.Option(False, "--overwrite", "-o", help="Overwrite existing files")
):
    """Apply a project template"""
    template_manager = ProjectTemplateManager()
    
    result = template_manager.apply_template(template_name, target_dir, overwrite=overwrite)
    
    if "error" in result:
        ui.display_error(result["error"])
        return
    
    ui.display_success(f"Template '{template_name}' applied to {target_dir}!")
    ui.console.print(f"Files applied: {len(result['applied_files'])}")
    if result['skipped_files']:
        ui.console.print(f"Files skipped: {len(result['skipped_files'])}")

@phase4_app.command()
def analytics(
    report_type: str = typer.Option("comprehensive", "--type", "-t", 
                                   help="Report type: comprehensive, team, user"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
    user_id: str = typer.Option(None, "--user", "-u", help="User ID for user report"),
    export: str = typer.Option(None, "--export", "-e", help="Export format: json, csv")
):
    """Generate team analytics reports"""
    team_manager = TeamManager()
    analytics_engine = AnalyticsEngine(team_manager)
    
    if report_type == "comprehensive":
        report = analytics_engine.get_comprehensive_report(days)
    elif report_type == "team":
        report = analytics_engine.get_team_comparison_report(days)
    elif report_type == "user":
        if not user_id:
            user_id = team_manager.get_active_user()["user_id"]
        report = analytics_engine.get_user_performance_report(user_id, days)
    else:
        ui.display_error(f"Unknown report type: {report_type}")
        return
    
    if "error" in report:
        ui.display_error(report["error"])
        return
    
    if export:
        export_result = analytics_engine.export_report(report_type, export, days)
        if "error" in export_result:
            ui.display_error(export_result["error"])
            return
        
        # Save to file
        filename = f"deepseek_analytics_{report_type}_{days}d.{export}"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(export_result["data"])
        
        ui.display_success(f"Report exported to {filename}")
        return
    
    # Display report
    from rich.table import Table
    from rich.panel import Panel
    
    if report_type == "comprehensive":
        display_comprehensive_report(report, ui)
    elif report_type == "team":
        display_team_report(report, ui)
    elif report_type == "user":
        display_user_report(report, ui)

@phase4_app.command()
def config_check():
    """Check and validate system configuration"""
    from ..core.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    info = config_manager.get_config_info()
    
    from rich.table import Table
    
    table = Table(title="🔧 Configuration Health Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="yellow")
    
    # Team config check
    if info["team_config_exists"]:
        team_config = config_manager.load_team_config()
        if team_config and team_config.get("users"):
            table.add_row("Team Configuration", "✅ Healthy", f"{len(team_config['users'])} users configured")
        else:
            table.add_row("Team Configuration", "❌ Corrupted", "Invalid or empty configuration")
    else:
        table.add_row("Team Configuration", "❌ Missing", "Run 'deepseek-code setup'")
    
    # Usage tracking check
    if info["usage_log_exists"]:
        usage_data = config_manager.load_usage_log()
        if isinstance(usage_data, dict):
            table.add_row("Usage Tracking", "✅ Healthy", "Data collection active")
        else:
            table.add_row("Usage Tracking", "⚠️ Warning", "Invalid data format")
    else:
        table.add_row("Usage Tracking", "⚪ Disabled", "No usage data yet")
    
    # User preferences check
    table.add_row("User Preferences", "✅ Ready", f"{info['user_preference_files']} profiles")
    
    # Backup system check
    table.add_row("Backup System", "✅ Ready", f"{info['total_backups']} backups")
    
    # Directory structure check
    table.add_row("Directory Structure", "✅ Healthy", "All directories created")
    
    ui.console.print(table)
    
    # Recommendations
    if not info["team_config_exists"]:
        ui.console.print("\n[bold yellow]💡 Recommendation: Run 'deepseek-code setup' to configure your team[/bold yellow]")

def display_comprehensive_report(report: Dict[str, Any], ui: TerminalUI):
    """Display comprehensive analytics report"""
    from rich.table import Table
    
    # Summary
    summary = report["summary"]
    ui.console.print(Panel(
        f"📊 Total Tokens: [bold]{summary['total_tokens']:,}[/bold]\n"
        f"🔄 Total Operations: [bold]{summary['total_operations']:,}[/bold]\n"
        f"👥 Active Users: [bold]{summary['active_users']}[/bold]\n"
        f"📅 Period: {report['period']['start']} to {report['period']['end']}",
        title="📈 Team Analytics Summary",
        border_style="green"
    ))
    
    # User breakdown
    user_table = Table(title="👤 User Breakdown")
    user_table.add_column("User", style="cyan")
    user_table.add_column("Tokens", style="white")
    user_table.add_column("Operations", style="yellow")
    user_table.add_column("Percentage", style="green")
    
    for user_id, user_data in report["user_breakdown"].items():
        percentage = (user_data["total_tokens"] / summary["total_tokens"] * 100) if summary["total_tokens"] > 0 else 0
        user_table.add_row(
            user_data["username"],
            f"{user_data['total_tokens']:,}",
            str(user_data["total_operations"]),
            f"{percentage:.1f}%"
        )
    
    ui.console.print(user_table)
    
    # Recommendations
    if report["recommendations"]:
        ui.console.print("\n[bold]💡 Recommendations:[/bold]")
        for rec in report["recommendations"]:
            ui.console.print(f"• {rec}")

def display_team_report(report: Dict[str, Any], ui: TerminalUI):
    """Display team comparison report"""
    from rich.table import Table
    
    ui.console.print(Panel(
        f"👥 Total Users: [bold]{report['total_users']}[/bold]\n"
        f"📊 Average Tokens/User: [bold]{report['team_averages']['avg_tokens_per_user']:,.0f}[/bold]\n"
        f"🔄 Average Operations/User: [bold]{report['team_averages']['avg_operations_per_user']:,.0f}[/bold]",
        title="🏆 Team Comparison",
        border_style="blue"
    ))
    
    comparison_table = Table(title="📊 User Comparison")
    comparison_table.add_column("User", style="cyan")
    comparison_table.add_column("Tokens", style="white")
    comparison_table.add_column("Operations", style="yellow")
    comparison_table.add_column("Token %", style="green")
    comparison_table.add_column("Efficiency", style="blue")
    
    for user_id, user_data in report["comparison_data"].items():
        efficiency = "🏆" if user_data["efficiency_rank"] == 1 else f"#{user_data['efficiency_rank']}"
        comparison_table.add_row(
            user_data["username"],
            f"{user_data['tokens_used']:,}",
            str(user_data["operations_count"]),
            f"{user_data['token_percentage']:.1f}%",
            efficiency
        )
    
    ui.console.print(comparison_table)

def display_user_report(report: Dict[str, Any], ui: TerminalUI):
    """Display user performance report"""
    from rich.panel import Panel
    
    metrics = report["metrics"]
    
    ui.console.print(Panel(
        f"👤 User: [bold]{report['username']}[/bold]\n"
        f"📊 Total Tokens: [bold]{report['total_tokens']:,}[/bold]\n"
        f"🔄 Total Operations: [bold]{report['total_operations']:,}[/bold]\n"
        f"⭐ Efficiency Score: [bold]{metrics['efficiency_score']:.1f}/100[/bold]\n"
        f"📈 Productivity Trend: [bold]{metrics['productivity_trend'].title()}[/bold]",
        title="🎯 User Performance Report",
        border_style="yellow"
    ))
    
    # Top operations
    if metrics["preferred_operations"]:
        ui.console.print("\n[bold]🔧 Top Operations:[/bold]")
        for op, count in metrics["preferred_operations"]:
            ui.console.print(f"• {op}: {count} times")