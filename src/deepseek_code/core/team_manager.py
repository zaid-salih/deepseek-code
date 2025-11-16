# deepseek-code/src/deepseek_code/core/team_manager.py
import os
import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet
import logging

class TeamManager:
    """3-user team management system"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.expanduser("~/.deepseek-code")
        self.team_config_path = os.path.join(self.config_dir, "team_config.json")
        self.usage_file = os.path.join(self.config_dir, "usage_log.json")
        self.key_file = os.path.join(self.config_dir, ".encryption_key")
        
        os.makedirs(self.config_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self._ensure_encryption_key()
    
    def _ensure_encryption_key(self):
        """Generate or load encryption key"""
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        with open(self.key_file, 'rb') as f:
            self.cipher = Fernet(f.read())
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key for use"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()
    
    def setup_team(self, api_key: str, team_name: str, users: List[Dict]) -> Dict:
        """Initial team setup with 3 users"""
        
        team_config = {
            "team_name": team_name,
            "team_id": f"team_{uuid.uuid4().hex[:8]}",
            "api_key": self.encrypt_api_key(api_key),
            "created_date": datetime.now().isoformat(),
            "active_user": users[0]["user_id"],
            "users": []
        }
        
        for i, user_data in enumerate(users):
            user = {
                "user_id": user_data["user_id"],
                "username": user_data["username"],
                "role": "admin" if i == 0 else "member",
                "preferences": user_data.get("preferences", {}),
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat()
            }
            team_config["users"].append(user)
            
            # Create user preferences file
            self._save_user_preferences(user["user_id"], user["preferences"])
        
        self._save_team_config(team_config)
        self._initialize_usage_tracking(team_config["users"])
        
        return team_config
    
    def switch_user(self, user_id: str) -> bool:
        """Switch active user context"""
        config = self._load_team_config()
        if not config:
            return False
        
        user_exists = any(user["user_id"] == user_id for user in config["users"])
        if user_exists:
            config["active_user"] = user_id
            # Update last active time
            for user in config["users"]:
                if user["user_id"] == user_id:
                    user["last_active"] = datetime.now().isoformat()
            
            self._save_team_config(config)
            return True
        return False
    
    def get_active_user(self) -> Optional[Dict]:
        """Get current active user"""
        config = self._load_team_config()
        if not config:
            return None
        
        active_id = config.get("active_user")
        for user in config["users"]:
            if user["user_id"] == active_id:
                return user
        return None
    
    def get_user_context(self) -> Optional[Dict]:
        """Get current user context with preferences"""
        user = self.get_active_user()
        if not user:
            return None
        
        preferences = self._load_user_preferences(user["user_id"])
        return {
            **user,
            "preferences": preferences
        }
    
    def track_usage(self, user_id: str, operation: str, tokens: int):
        """Track API usage per user"""
        usage_data = self._load_usage_data()
        
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in usage_data:
            usage_data[today] = {}
        
        if user_id not in usage_data[today]:
            usage_data[today][user_id] = {
                "tokens_used": 0,
                "operations": {}
            }
        
        usage_data[today][user_id]["tokens_used"] += tokens
        usage_data[today][user_id]["operations"][operation] = \
            usage_data[today][user_id]["operations"].get(operation, 0) + 1
        
        self._save_usage_data(usage_data)
    
    def get_team_usage(self) -> Dict:
        """Get usage statistics for the team"""
        return self._load_usage_data()
    
    def get_user_usage(self, user_id: str) -> Dict:
        """Get individual user usage"""
        usage_data = self._load_usage_data()
        user_usage = {}
        
        for date, daily_usage in usage_data.items():
            if user_id in daily_usage:
                user_usage[date] = daily_usage[user_id]
        
        return user_usage
    
    def _save_team_config(self, config: Dict):
        """Save team configuration"""
        with open(self.team_config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _load_team_config(self) -> Optional[Dict]:
        """Load team configuration"""
        if not os.path.exists(self.team_config_path):
            return None
        
        try:
            with open(self.team_config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def _save_user_preferences(self, user_id: str, preferences: Dict):
        """Save user preferences"""
        pref_file = os.path.join(self.config_dir, f"user_preferences_{user_id}.json")
        with open(pref_file, 'w') as f:
            json.dump(preferences, f, indent=2)
    
    def _load_user_preferences(self, user_id: str) -> Dict:
        """Load user preferences"""
        pref_file = os.path.join(self.config_dir, f"user_preferences_{user_id}.json")
        if os.path.exists(pref_file):
            try:
                with open(pref_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {}
    
    def _initialize_usage_tracking(self, users: List[Dict]):
        """Initialize usage tracking for all users"""
        usage_data = {}
        for user in users:
            usage_data[user["user_id"]] = {
                "tokens_used": 0,
                "operations": {}
            }
        self._save_usage_data({})
    
    def _save_usage_data(self, usage_data: Dict):
        """Save usage data"""
        with open(self.usage_file, 'w') as f:
            json.dump(usage_data, f, indent=2)
    
    def _load_usage_data(self) -> Dict:
        """Load usage data"""
        if not os.path.exists(self.usage_file):
            return {}
        
        try:
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}