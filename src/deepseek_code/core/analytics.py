# deepseek-code/src/deepseek_code/core/analytics.py
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging
import statistics

class AnalyticsEngine:
    """Advanced usage analytics and reporting"""
    
    def __init__(self, team_manager):
        self.team_manager = team_manager
        self.logger = logging.getLogger(__name__)
    
    def get_comprehensive_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        
        usage_data = self.team_manager.get_team_usage()
        team_config = self.team_manager._load_team_config()
        
        if not team_config:
            return {"error": "Team configuration not found"}
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        report = {
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "days": days
            },
            "summary": {
                "total_tokens": 0,
                "total_operations": 0,
                "active_users": 0,
                "busiest_day": None,
                "most_used_operation": None
            },
            "user_breakdown": {},
            "daily_trends": {},
            "operation_analytics": {},
            "recommendations": []
        }
        
        # Process usage data
        daily_tokens = {}
        operation_counts = {}
        user_activity = {}
        
        for date_str, daily_usage in usage_data.items():
            current_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= current_date <= end_date:
                daily_total = 0
                
                for user_id, user_usage in daily_usage.items():
                    user_tokens = user_usage.get("tokens_used", 0)
                    daily_total += user_tokens
                    
                    # User breakdown
                    if user_id not in report["user_breakdown"]:
                        username = self._get_username(user_id, team_config)
                        report["user_breakdown"][user_id] = {
                            "username": username,
                            "total_tokens": 0,
                            "total_operations": 0,
                            "operations": {}
                        }
                    
                    report["user_breakdown"][user_id]["total_tokens"] += user_tokens
                    report["summary"]["total_tokens"] += user_tokens
                    
                    # Operation counts
                    for op, count in user_usage.get("operations", {}).items():
                        report["user_breakdown"][user_id]["total_operations"] += count
                        report["user_breakdown"][user_id]["operations"][op] = \
                            report["user_breakdown"][user_id]["operations"].get(op, 0) + count
                        
                        report["summary"]["total_operations"] += count
                        operation_counts[op] = operation_counts.get(op, 0) + count
                
                daily_tokens[date_str] = daily_total
        
        # Calculate analytics
        if daily_tokens:
            report["summary"]["busiest_day"] = max(daily_tokens, key=daily_tokens.get)
            report["daily_trends"] = daily_tokens
        
        if operation_counts:
            report["summary"]["most_used_operation"] = max(operation_counts, key=operation_counts.get)
            report["operation_analytics"] = operation_counts
        
        # User activity
        active_users = len([user for user in report["user_breakdown"].values() 
                          if user["total_tokens"] > 0])
        report["summary"]["active_users"] = active_users
        
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def get_user_performance_report(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Generate detailed performance report for a user"""
        
        team_report = self.get_comprehensive_report(days)
        if "error" in team_report:
            return team_report
        
        user_data = team_report["user_breakdown"].get(user_id, {})
        if not user_data:
            return {"error": f"No data found for user {user_id}"}
        
        # Calculate user-specific metrics
        user_metrics = {
            "efficiency_score": self._calculate_efficiency_score(user_data),
            "productivity_trend": self._calculate_productivity_trend(user_id, days),
            "preferred_operations": sorted(
                user_data.get("operations", {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Top 5 operations
        }
        
        return {
            "user_id": user_id,
            "username": user_data.get("username", "Unknown"),
            "period": team_report["period"],
            **user_data,
            "metrics": user_metrics
        }
    
    def get_team_comparison_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate team comparison report"""
        
        team_report = self.get_comprehensive_report(days)
        if "error" in team_report:
            return team_report
        
        user_breakdown = team_report["user_breakdown"]
        
        # Calculate comparative metrics
        total_tokens = team_report["summary"]["total_tokens"]
        user_counts = len(user_breakdown)
        
        comparison_data = {}
        for user_id, user_data in user_breakdown.items():
            user_tokens = user_data["total_tokens"]
            user_operations = user_data["total_operations"]
            
            comparison_data[user_id] = {
                "username": user_data["username"],
                "tokens_used": user_tokens,
                "operations_count": user_operations,
                "token_percentage": (user_tokens / total_tokens * 100) if total_tokens > 0 else 0,
                "avg_tokens_per_operation": user_tokens / user_operations if user_operations > 0 else 0,
                "efficiency_rank": 0  # Will be calculated below
            }
        
        # Calculate efficiency ranks
        efficiency_scores = [
            (user_id, data["avg_tokens_per_operation"]) 
            for user_id, data in comparison_data.items() 
            if data["avg_tokens_per_operation"] > 0
        ]
        
        if efficiency_scores:
            # Lower tokens per operation is better (more efficient)
            sorted_scores = sorted(efficiency_scores, key=lambda x: x[1])
            for rank, (user_id, _) in enumerate(sorted_scores, 1):
                comparison_data[user_id]["efficiency_rank"] = rank
        
        return {
            "period": team_report["period"],
            "total_users": user_counts,
            "comparison_data": comparison_data,
            "team_averages": {
                "avg_tokens_per_user": total_tokens / user_counts if user_counts > 0 else 0,
                "avg_operations_per_user": team_report["summary"]["total_operations"] / user_counts if user_counts > 0 else 0
            }
        }
    
    def export_report(self, report_type: str = "comprehensive", format: str = "json", days: int = 30) -> Dict[str, Any]:
        """Export analytics report in various formats"""
        
        if report_type == "comprehensive":
            report = self.get_comprehensive_report(days)
        elif report_type == "team_comparison":
            report = self.get_team_comparison_report(days)
        else:
            return {"error": f"Unknown report type: {report_type}"}
        
        if "error" in report:
            return report
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "report_type": report_type,
            "period": report["period"],
            "data": report
        }
        
        if format == "json":
            return {
                "success": True,
                "format": "json",
                "data": json.dumps(export_data, indent=2)
            }
        elif format == "csv":
            # Simplified CSV export for key metrics
            csv_data = self._convert_to_csv(export_data)
            return {
                "success": True,
                "format": "csv", 
                "data": csv_data
            }
        else:
            return {"error": f"Unsupported format: {format}"}
    
    def _get_username(self, user_id: str, team_config: Dict[str, Any]) -> str:
        """Get username from user ID"""
        for user in team_config.get("users", []):
            if user["user_id"] == user_id:
                return user["username"]
        return user_id
    
    def _calculate_efficiency_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate user efficiency score (0-100)"""
        tokens = user_data.get("total_tokens", 0)
        operations = user_data.get("total_operations", 0)
        
        if operations == 0:
            return 0.0
        
        # Lower tokens per operation is better
        tokens_per_op = tokens / operations
        
        # Normalize to 0-100 scale (assuming < 100 tokens/op is excellent)
        score = max(0, 100 - (tokens_per_op / 100 * 100))
        return min(100, score)
    
    def _calculate_productivity_trend(self, user_id: str, days: int) -> str:
        """Calculate productivity trend for a user"""
        # This would analyze daily usage patterns
        # Simplified implementation
        usage_data = self.team_manager.get_team_usage()
        
        recent_days = 7
        previous_days = 14
        
        recent_tokens = 0
        previous_tokens = 0
        
        end_date = datetime.now()
        
        for i in range(recent_days):
            date_str = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            if date_str in usage_data and user_id in usage_data[date_str]:
                recent_tokens += usage_data[date_str][user_id].get("tokens_used", 0)
        
        for i in range(recent_days, previous_days):
            date_str = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            if date_str in usage_data and user_id in usage_data[date_str]:
                previous_tokens += usage_data[date_str][user_id].get("tokens_used", 0)
        
        if previous_tokens == 0:
            return "stable"
        
        change_percent = ((recent_tokens - previous_tokens) / previous_tokens) * 100
        
        if change_percent > 20:
            return "increasing"
        elif change_percent < -20:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate intelligent recommendations based on analytics"""
        recommendations = []
        
        total_tokens = report["summary"]["total_tokens"]
        active_users = report["summary"]["active_users"]
        
        # Token usage recommendations
        if total_tokens > 100000:  # High usage threshold
            recommendations.append("Consider optimizing token usage by using more specific prompts")
        
        if active_users < 2:
            recommendations.append("Encourage more team members to use the system for better collaboration")
        
        # Operation-specific recommendations
        operations = report["operation_analytics"]
        if operations.get("refactoring", 0) < operations.get("chat_completion", 0) / 10:
            recommendations.append("Team might benefit from more refactoring operations to maintain code quality")
        
        # Efficiency recommendations
        for user_id, user_data in report["user_breakdown"].items():
            efficiency = self._calculate_efficiency_score(user_data)
            if efficiency < 50:
                username = user_data["username"]
                recommendations.append(f"{username} might benefit from prompt optimization training")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _convert_to_csv(self, report_data: Dict[str, Any]) -> str:
        """Convert report data to CSV format"""
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Metric", "Value"])
        
        # Write summary data
        summary = report_data["data"]["summary"]
        writer.writerow(["Total Tokens", summary["total_tokens"]])
        writer.writerow(["Total Operations", summary["total_operations"]])
        writer.writerow(["Active Users", summary["active_users"]])
        writer.writerow(["Busiest Day", summary["busiest_day"]])
        writer.writerow(["Most Used Operation", summary["most_used_operation"]])
        
        writer.writerow([])  # Empty row
        
        # Write user breakdown
        writer.writerow(["User Breakdown"])
        writer.writerow(["Username", "Tokens Used", "Operations", "Token Percentage"])
        
        for user_id, user_data in report_data["data"]["user_breakdown"].items():
            writer.writerow([
                user_data["username"],
                user_data["total_tokens"],
                user_data["total_operations"],
                f"{(user_data['total_tokens'] / summary['total_tokens'] * 100):.1f}%" if summary['total_tokens'] > 0 else "0%"
            ])
        
        return output.getvalue()