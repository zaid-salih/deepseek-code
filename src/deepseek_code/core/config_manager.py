# deepseek-code/src/deepseek_code/core/config_manager.py
import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    """Configuration management for DeepSeek-Code"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or os.path.expanduser("~/.deepseek-code"))
        self.team_config_path = self.config_dir / "team_config.json"
        self.usage_log_path = self.config_dir / "usage_log.json"
        self.backup_dir = self.config_dir / "backups"
        
        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
    
    def initialize_config_structure(self) -> bool:
        """Initialize the complete configuration structure"""
        try:
            # Create default team config if doesn't exist
            if not self.team_config_path.exists():
                default_team_config = {
                    "team_name": "MyDevTeam",
                    "team_id": "team_default",
                    "api_key": "",
                    "created_date": "2024-01-01T00:00:00Z",
                    "active_user": "user_admin",
                    "users": [
                        {
                            "user_id": "user_admin",
                            "username": "admin",
                            "role": "admin",
                            "preferences": {},
                            "created_at": "2024-01-01T00:00:00Z",
                            "last_active": "2024-01-01T00:00:00Z"
                        }
                    ]
                }
                self.save_team_config(default_team_config)
            
            # Create default usage log
            if not self.usage_log_path.exists():
                self.save_usage_log({})
            
            # Create default user preferences
            self._initialize_default_user_preferences()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize config structure: {e}")
            return False
    
    def save_team_config(self, config: Dict[str, Any]) -> bool:
        """Save team configuration with backup"""
        try:
            # Create backup of existing config
            if self.team_config_path.exists():
                backup_path = self.backup_dir / f"team_config_backup_{len(list(self.backup_dir.glob('team_config_backup_*')))}.json"
                shutil.copy2(self.team_config_path, backup_path)
            
            with open(self.team_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to save team config: {e}")
            return False
    
    def load_team_config(self) -> Optional[Dict[str, Any]]:
        """Load team configuration"""
        try:
            if not self.team_config_path.exists():
                return None
            
            with open(self.team_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load team config: {e}")
            return None
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Save user preferences"""
        try:
            pref_file = self.config_dir / f"user_preferences_{user_id}.json"
            
            # Backup existing preferences
            if pref_file.exists():
                backup_path = self.backup_dir / f"user_preferences_{user_id}_backup_{len(list(self.backup_dir.glob(f'user_preferences_{user_id}_backup_*')))}.json"
                shutil.copy2(pref_file, backup_path)
            
            with open(pref_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to save user preferences for {user_id}: {e}")
            return False
    
    def load_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Load user preferences"""
        try:
            pref_file = self.config_dir / f"user_preferences_{user_id}.json"
            if not pref_file.exists():
                return self._get_default_preferences()
            
            with open(pref_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load user preferences for {user_id}: {e}")
            return self._get_default_preferences()
    
    def save_usage_log(self, usage_data: Dict[str, Any]) -> bool:
        """Save usage log"""
        try:
            with open(self.usage_log_path, 'w', encoding='utf-8') as f:
                json.dump(usage_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save usage log: {e}")
            return False
    
    def load_usage_log(self) -> Dict[str, Any]:
        """Load usage log"""
        try:
            if not self.usage_log_path.exists():
                return {}
            
            with open(self.usage_log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load usage log: {e}")
            return {}
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration information"""
        team_config = self.load_team_config() or {}
        usage_log = self.load_usage_log()
        
        user_files = list(self.config_dir.glob("user_preferences_*.json"))
        
        return {
            "config_dir": str(self.config_dir),
            "team_config_exists": self.team_config_path.exists(),
            "usage_log_exists": self.usage_log_path.exists(),
            "user_preference_files": len(user_files),
            "team_name": team_config.get("team_name", "Not configured"),
            "user_count": len(team_config.get("users", [])),
            "total_backups": len(list(self.backup_dir.glob("*.json")))
        }
    
    def _initialize_default_user_preferences(self):
        """Initialize default user preferences for existing users"""
        team_config = self.load_team_config()
        if not team_config:
            return
        
        for user in team_config.get("users", []):
            user_id = user["user_id"]
            pref_file = self.config_dir / f"user_preferences_{user_id}.json"
            
            if not pref_file.exists():
                default_prefs = self._get_default_preferences()
                self.save_user_preferences(user_id, default_prefs)
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            "theme": "dark",
            "default_language": "python",
            "code_style": "pep8",
            "auto_save": True,
            "max_file_size": 10000,
            "enable_syntax_highlighting": True,
            "show_line_numbers": True,
            "auto_format_on_save": False,
            "preferred_ide": "vscode",
            "git_auto_commit": False,
            "ai_model": "deepseek-coder",
            "temperature": 0.7,
            "max_tokens": 2048
        }