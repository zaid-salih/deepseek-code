# deepseek-code/src/deepseek_code/core/file_manager.py
import os
import glob
import fnmatch
from typing import List, Dict, Optional
from pathlib import Path
import logging

class FileManager:
    """Cross-platform file operations and project context management"""
    
    def __init__(self, root_path: str = None):
        self.root_path = root_path or os.getcwd()
        self.ignore_patterns = self._load_gitignore_patterns()
        self.logger = logging.getLogger(__name__)
    
    def discover_project_structure(self, max_files: int = 1000) -> Dict:
        """Discover and map project structure"""
        project_structure = {
            "root": self.root_path,
            "files": [],
            "directories": [],
            "file_types": {},
            "total_size": 0
        }
        
        file_count = 0
        for root, dirs, files in os.walk(self.root_path):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_ignored(file_path):
                    continue
                
                if file_count >= max_files:
                    break
                
                file_info = self._get_file_info(file_path)
                project_structure["files"].append(file_info)
                project_structure["total_size"] += file_info.get("size", 0)
                
                # Count file types
                ext = file_info["extension"]
                project_structure["file_types"][ext] = project_structure["file_types"].get(ext, 0) + 1
                
                file_count += 1
            
            if file_count >= max_files:
                break
        
        return project_structure
    
    def read_file(self, file_path: str, max_size: int = 100000) -> Optional[str]:
        """Read file content with size limit"""
        try:
            full_path = self._resolve_path(file_path)
            if not os.path.exists(full_path):
                return None
            
            file_size = os.path.getsize(full_path)
            if file_size > max_size:
                self.logger.warning(f"File {file_path} exceeds size limit ({file_size} > {max_size})")
                return None
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except (IOError, UnicodeDecodeError) as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def write_file(self, file_path: str, content: str, backup: bool = True) -> bool:
        """Write content to file with optional backup"""
        try:
            full_path = self._resolve_path(file_path)
            
            if backup and os.path.exists(full_path):
                backup_path = f"{full_path}.backup"
                import shutil
                shutil.copy2(full_path, backup_path)
            
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except IOError as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    def find_files(self, 
                   pattern: str = "*", 
                   file_type: str = None,
                   content_search: str = None) -> List[Dict]:
        """Find files matching criteria"""
        matches = []
        
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_ignored(file_path):
                    continue
                
                # Pattern matching
                if not fnmatch.fnmatch(file, pattern):
                    continue
                
                # File type filtering
                if file_type and not file.endswith(file_type):
                    continue
                
                # Content search
                if content_search:
                    content = self.read_file(file_path)
                    if content and content_search in content:
                        matches.append(self._get_file_info(file_path))
                else:
                    matches.append(self._get_file_info(file_path))
        
        return matches
    
    def get_file_tree(self, max_depth: int = 3) -> Dict:
        """Get hierarchical file tree structure"""
        def build_tree(path, depth=0):
            if depth > max_depth:
                return None
            
            if self._is_ignored(path):
                return None
            
            name = os.path.basename(path)
            node = {"name": name, "path": path, "type": "directory" if os.path.isdir(path) else "file"}
            
            if os.path.isdir(path):
                node["children"] = []
                try:
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        child_node = build_tree(item_path, depth + 1)
                        if child_node:
                            node["children"].append(child_node)
                except PermissionError:
                    pass
            
            return node
        
        return build_tree(self.root_path)
    
    def _get_file_info(self, file_path: str) -> Dict:
        """Get detailed file information"""
        stat = os.stat(file_path)
        _, ext = os.path.splitext(file_path)
        
        return {
            "path": file_path,
            "name": os.path.basename(file_path),
            "extension": ext.lower(),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_directory": os.path.isdir(file_path)
        }
    
    def _load_gitignore_patterns(self) -> List[str]:
        """Load .gitignore patterns"""
        gitignore_path = os.path.join(self.root_path, ".gitignore")
        patterns = [
            ".git/", "node_modules/", "__pycache__/", "*.pyc", 
            ".DS_Store", "*.log", "dist/", "build/"
        ]
        
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except IOError:
                pass
        
        return patterns
    
    def _is_ignored(self, path: str) -> bool:
        """Check if path matches ignore patterns"""
        rel_path = os.path.relpath(path, self.root_path)
        if rel_path == '.':
            return False
        
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
            if pattern.endswith('/') and rel_path.startswith(pattern):
                return True
        
        return False
    
    def _resolve_path(self, file_path: str) -> str:
        """Resolve relative or absolute path"""
        if os.path.isabs(file_path):
            return file_path
        return os.path.join(self.root_path, file_path)