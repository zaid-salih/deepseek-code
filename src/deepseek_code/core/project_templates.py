# deepseek-code/src/deepseek_code/core/project_templates.py
import os
import json
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

class ProjectTemplateManager:
    """Shared project templates for team collaboration"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = Path(config_dir or os.path.expanduser("~/.deepseek-code"))
        self.templates_dir = self.config_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def create_template(self, 
                       template_name: str, 
                       description: str,
                       files: Dict[str, str],
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new project template"""
        
        template_dir = self.templates_dir / template_name
        template_dir.mkdir(exist_ok=True)
        
        template_info = {
            "name": template_name,
            "description": description,
            "created_by": self._get_current_user(),
            "created_at": self._get_timestamp(),
            "files": list(files.keys()),
            "metadata": metadata or {}
        }
        
        # Save template info
        with open(template_dir / "template.json", 'w', encoding='utf-8') as f:
            json.dump(template_info, f, indent=2)
        
        # Save template files
        for file_path, content in files.items():
            full_path = template_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return {
            "success": True,
            "template_name": template_name,
            "files_created": len(files),
            "template_dir": str(template_dir)
        }
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        templates = []
        
        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir():
                info_file = template_dir / "template.json"
                if info_file.exists():
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            template_info = json.load(f)
                            templates.append(template_info)
                    except json.JSONDecodeError:
                        continue
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template with all files"""
        template_dir = self.templates_dir / template_name
        if not template_dir.exists():
            return None
        
        info_file = template_dir / "template.json"
        if not info_file.exists():
            return None
        
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                template_info = json.load(f)
        except json.JSONDecodeError:
            return None
        
        # Load all file contents
        files_content = {}
        for file_path in template_info["files"]:
            full_path = template_dir / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        files_content[file_path] = f.read()
                except Exception as e:
                    self.logger.error(f"Error reading template file {file_path}: {e}")
        
        template_info["files_content"] = files_content
        return template_info
    
    def apply_template(self, 
                      template_name: str, 
                      target_dir: str,
                      variables: Dict[str, str] = None,
                      overwrite: bool = False) -> Dict[str, Any]:
        """Apply a template to a target directory"""
        
        template = self.get_template(template_name)
        if not template:
            return {"error": f"Template '{template_name}' not found"}
        
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)
        
        applied_files = []
        skipped_files = []
        
        for file_path, content in template["files_content"].items():
            # Replace variables in content
            if variables:
                for key, value in variables.items():
                    placeholder = f"{{{{ {key} }}}}"
                    content = content.replace(placeholder, value)
            
            full_target_path = target_path / file_path
            
            # Check if file exists
            if full_target_path.exists() and not overwrite:
                skipped_files.append(file_path)
                continue
            
            # Create directory if needed
            full_target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            applied_files.append(file_path)
        
        return {
            "success": True,
            "template_applied": template_name,
            "target_directory": str(target_path),
            "applied_files": applied_files,
            "skipped_files": skipped_files,
            "total_files": len(applied_files) + len(skipped_files)
        }
    
    def delete_template(self, template_name: str) -> Dict[str, Any]:
        """Delete a template"""
        template_dir = self.templates_dir / template_name
        
        if not template_dir.exists():
            return {"error": f"Template '{template_name}' not found"}
        
        try:
            shutil.rmtree(template_dir)
            return {
                "success": True,
                "message": f"Template '{template_name}' deleted"
            }
        except Exception as e:
            return {"error": f"Failed to delete template: {e}"}
    
    def create_from_existing_project(self, 
                                   template_name: str,
                                   source_dir: str,
                                   description: str,
                                   include_patterns: List[str] = None,
                                   exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """Create a template from an existing project"""
        
        if include_patterns is None:
            include_patterns = ["*.py", "*.js", "*.ts", "*.json", "*.md", "*.txt"]
        
        if exclude_patterns is None:
            exclude_patterns = [".git", "__pycache__", "node_modules", "*.pyc"]
        
        source_path = Path(source_dir)
        if not source_path.exists():
            return {"error": f"Source directory '{source_dir}' not found"}
        
        files_content = {}
        
        for pattern in include_patterns:
            for file_path in source_path.rglob(pattern):
                # Check exclusion patterns
                if any(excluded in str(file_path) for excluded in exclude_patterns):
                    continue
                
                if file_path.is_file():
                    try:
                        relative_path = file_path.relative_to(source_path)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            files_content[str(relative_path)] = f.read()
                    except Exception as e:
                        self.logger.warning(f"Could not read {file_path}: {e}")
        
        return self.create_template(template_name, description, files_content)
    
    def _get_current_user(self) -> str:
        """Get current username"""
        try:
            import getpass
            return getpass.getuser()
        except:
            return "unknown"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()