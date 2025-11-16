# deepseek-code/src/deepseek_code/core/code_review.py
import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
from .ai_engine import DeepSeekAI
from .team_manager import TeamManager
from .git_integration import GitIntegration

class CodeReviewManager:
    """Code review automation system for team collaboration"""
    
    def __init__(self, team_manager: TeamManager, ai_engine: DeepSeekAI):
        self.team_manager = team_manager
        self.ai_engine = ai_engine
        self.reviews_dir = Path("~/.deepseek-code/code_reviews").expanduser()
        self.reviews_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def request_review(self, 
                      file_path: str, 
                      reviewer_id: str,
                      instructions: str = "",
                      priority: str = "normal") -> Dict[str, Any]:
        """Request code review from team member"""
        
        # Validate reviewer
        team_config = self.team_manager._load_team_config()
        if not team_config:
            return {"error": "Team configuration not found"}
        
        reviewer_exists = any(user["user_id"] == reviewer_id for user in team_config["users"])
        if not reviewer_exists:
            return {"error": f"Reviewer {reviewer_id} not found in team"}
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        # Create review request
        review_id = str(uuid.uuid4())[:8]
        review_data = {
            "review_id": review_id,
            "file_path": file_path,
            "requester_id": self.team_manager.get_active_user()["user_id"],
            "reviewer_id": reviewer_id,
            "instructions": instructions,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "code_snippet": code_content[:5000]  # Limit code size
        }
        
        # Save review request
        review_file = self.reviews_dir / f"review_{review_id}.json"
        with open(review_file, 'w', encoding='utf-8') as f:
            json.dump(review_data, f, indent=2)
        
        # Track usage
        self.team_manager.track_usage(
            self.team_manager.get_active_user()["user_id"],
            "review_request",
            50  # Token estimate
        )
        
        return {
            "success": True,
            "review_id": review_id,
            "message": f"Review requested from {reviewer_id}",
            "review_file": str(review_file)
        }
    
    def automated_review(self, 
                        code_changes: Dict[str, Any],
                        rules: List[str] = None) -> Dict[str, Any]:
        """AI-powered automated code review"""
        
        if rules is None:
            rules = [
                "code_quality",
                "security",
                "performance", 
                "best_practices",
                "maintainability"
            ]
        
        code_content = code_changes.get('code', '')
        language = code_changes.get('language', 'python')
        context = code_changes.get('context', '')
        
        prompt = f"""
        Perform a comprehensive code review focusing on: {', '.join(rules)}
        
        Code Language: {language}
        Context: {context}
        
        Code to review:
        ```{language}
        {code_content}
        ```
        
        Provide a structured review with:
        1. Critical issues (blockers)
        2. Major issues (should fix)
        3. Minor issues (could fix)
        4. Suggestions for improvement
        5. Security considerations
        
        Format the response as JSON.
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert code reviewer. Provide detailed, constructive feedback in JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = list(self.ai_engine.chat_completion(messages, stream=False))[0]
            
            # Parse JSON response
            try:
                review_data = json.loads(response)
            except json.JSONDecodeError:
                # If not JSON, structure it manually
                review_data = {
                    "summary": "AI Code Review",
                    "critical_issues": [],
                    "major_issues": [], 
                    "minor_issues": [],
                    "suggestions": [],
                    "security_notes": [],
                    "raw_response": response
                }
            
            # Track usage
            self.team_manager.track_usage(
                self.team_manager.get_active_user()["user_id"],
                "automated_review",
                len(response.split())  # Rough token estimate
            )
            
            return {
                "success": True,
                "review": review_data,
                "rules_checked": rules
            }
            
        except Exception as e:
            return {"error": f"Automated review failed: {e}"}
    
    def review_workflow(self, pr_url: str) -> Dict[str, Any]:
        """GitHub PR review automation workflow"""
        
        # Extract PR information (simplified)
        pr_parts = pr_url.split('/')
        if len(pr_parts) < 5:
            return {"error": "Invalid PR URL format"}
        
        # This would integrate with GitHub API in a real implementation
        pr_info = {
            "pr_url": pr_url,
            "repository": f"{pr_parts[-4]}/{pr_parts[-3]}",
            "pr_number": pr_parts[-1],
            "status": "pending_review"
        }
        
        # Create PR review workflow
        workflow_id = str(uuid.uuid4())[:8]
        workflow_data = {
            "workflow_id": workflow_id,
            "pr_info": pr_info,
            "assigned_reviewers": [],
            "automated_review": {},
            "team_reviews": [],
            "status": "initialized",
            "created_at": datetime.now().isoformat()
        }
        
        # Save workflow
        workflow_file = self.reviews_dir / f"pr_workflow_{workflow_id}.json"
        with open(workflow_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2)
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "pr_info": pr_info,
            "message": "PR review workflow initialized"
        }
    
    def get_pending_reviews(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get pending reviews for a user"""
        if user_id is None:
            user_id = self.team_manager.get_active_user()["user_id"]
        
        pending_reviews = []
        
        for review_file in self.reviews_dir.glob("review_*.json"):
            try:
                with open(review_file, 'r', encoding='utf-8') as f:
                    review_data = json.load(f)
                
                if (review_data.get('reviewer_id') == user_id and 
                    review_data.get('status') == 'pending'):
                    pending_reviews.append(review_data)
                    
            except (json.JSONDecodeError, KeyError):
                continue
        
        return pending_reviews
    
    def submit_review_feedback(self, 
                             review_id: str, 
                             feedback: str,
                             status: str = "approved") -> Dict[str, Any]:
        """Submit review feedback"""
        
        review_file = self.reviews_dir / f"review_{review_id}.json"
        if not review_file.exists():
            return {"error": f"Review {review_id} not found"}
        
        try:
            with open(review_file, 'r', encoding='utf-8') as f:
                review_data = json.load(f)
            
            # Update review
            review_data.update({
                "status": status,
                "feedback": feedback,
                "reviewed_at": datetime.now().isoformat(),
                "reviewer_id": self.team_manager.get_active_user()["user_id"],
                "updated_at": datetime.now().isoformat()
            })
            
            with open(review_file, 'w', encoding='utf-8') as f:
                json.dump(review_data, f, indent=2)
            
            return {
                "success": True,
                "review_id": review_id,
                "status": status,
                "message": "Review feedback submitted"
            }
            
        except Exception as e:
            return {"error": f"Failed to submit feedback: {e}"}
    
    def get_review_stats(self) -> Dict[str, Any]:
        """Get code review statistics for the team"""
        reviews = []
        
        for review_file in self.reviews_dir.glob("review_*.json"):
            try:
                with open(review_file, 'r', encoding='utf-8') as f:
                    reviews.append(json.load(f))
            except (json.JSONDecodeError, KeyError):
                continue
        
        stats = {
            "total_reviews": len(reviews),
            "pending_reviews": 0,
            "approved_reviews": 0,
            "rejected_reviews": 0,
            "by_reviewer": {},
            "by_requester": {}
        }
        
        for review in reviews:
            status = review.get('status', 'pending')
            reviewer = review.get('reviewer_id', 'unknown')
            requester = review.get('requester_id', 'unknown')
            
            if status == 'pending':
                stats["pending_reviews"] += 1
            elif status == 'approved':
                stats["approved_reviews"] += 1
            elif status == 'rejected':
                stats["rejected_reviews"] += 1
            
            # Count by reviewer
            stats["by_reviewer"][reviewer] = stats["by_reviewer"].get(reviewer, 0) + 1
            stats["by_requester"][requester] = stats["by_requester"].get(requester, 0) + 1
        
        return stats