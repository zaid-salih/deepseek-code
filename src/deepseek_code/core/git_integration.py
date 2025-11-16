# deepseek-code/src/deepseek_code/core/git_integration.py
import os
import subprocess
import json
from typing import Dict, List, Optional, Tuple, Any, Any
from pathlib import Path
import logging

class GitIntegration:
    """Git operations wrapper for DeepSeek-Code"""
    
    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path or os.getcwd())
        self.logger = logging.getLogger(__name__)
    
    def run_git_command(self, args: List[str], capture_output: bool = True) -> Tuple[bool, str, str]:
        """Run a git command and return results"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            self.logger.error(f"Git command failed: {e}")
            return False, "", str(e)
    
    def get_status(self) -> Dict[str, Any]:
        """Get git status with detailed information"""
        success, stdout, stderr = self.run_git_command(['status', '--porcelain', '-b'])
        
        if not success:
            return {"error": stderr}
        
        files = []
        for line in stdout.splitlines():
            if line.startswith('##'):
                continue  # Skip branch info line
            
            if line.strip():
                status = line[:2]
                file_path = line[3:]
                file_type = 'modified'
                
                if status.startswith('??'):
                    file_type = 'untracked'
                elif status.startswith('A'):
                    file_type = 'added'
                elif status.startswith('D'):
                    file_type = 'deleted'
                elif status.startswith('R'):
                    file_type = 'renamed'
                
                files.append({
                    'status': status.strip(),
                    'path': file_path,
                    'type': file_type
                })
        
        # Get branch information
        branch_success, branch_out, _ = self.run_git_command(['branch', '--show-current'])
        current_branch = branch_out.strip() if branch_success else "unknown"
        
        return {
            'current_branch': current_branch,
            'files': files,
            'has_changes': len(files) > 0
        }
    
    def get_branches(self) -> Dict[str, Any]:
        """Get list of all branches"""
        success, stdout, stderr = self.run_git_command(['branch', '-a', '--format=%(refname:short) %(objectname) %(upstream:short)'])
        
        if not success:
            return {"error": stderr}
        
        branches = []
        current_branch = None
        
        for line in stdout.splitlines():
            if line.strip():
                parts = line.split()
                branch_name = parts[0]
                commit_hash = parts[1] if len(parts) > 1 else ""
                upstream = parts[2] if len(parts) > 2 else ""
                
                is_current = branch_name.startswith('*')
                if is_current:
                    branch_name = branch_name[1:].strip()
                    current_branch = branch_name
                
                branches.append({
                    'name': branch_name,
                    'current': is_current,
                    'commit': commit_hash[:8],
                    'upstream': upstream
                })
        
        return {
            'branches': branches,
            'current_branch': current_branch
        }
    
    def get_commits(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent commits"""
        success, stdout, stderr = self.run_git_command([
            'log', 
            f'-{limit}', 
            '--oneline', 
            '--format=%H|%an|%ae|%ad|%s',
            '--date=short'
        ])
        
        if not success:
            return {"error": stderr}
        
        commits = []
        for line in stdout.splitlines():
            if line.strip():
                parts = line.split('|', 4)
                if len(parts) == 5:
                    commits.append({
                        'hash': parts[0],
                        'hash_short': parts[0][:7],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    })
        
        return {'commits': commits}
    
    def commit(self, message: str, files: List[str] = None) -> Dict[str, Any]:
        """Commit changes with AI-generated message"""
        if not files:
            # Add all changes
            add_success, _, add_stderr = self.run_git_command(['add', '.'])
            if not add_success:
                return {"error": f"Failed to add files: {add_stderr}"}
        else:
            for file in files:
                add_success, _, add_stderr = self.run_git_command(['add', file])
                if not add_success:
                    return {"error": f"Failed to add file {file}: {add_stderr}"}
        
        commit_success, commit_stdout, commit_stderr = self.run_git_command(['commit', '-m', message])
        
        return {
            'success': commit_success,
            'message': commit_stdout if commit_success else commit_stderr,
            'commit_message': message
        }
    
    def generate_commit_message(self, changes: Dict[str, Any]) -> str:
        """Generate AI-powered commit message"""
        # This would be enhanced with AI in the future
        file_count = len(changes.get('files', []))
        file_types = {}
        
        for file in changes.get('files', []):
            ext = Path(file['path']).suffix
            file_types[ext] = file_types.get(ext, 0) + 1
        
        if file_count == 1:
            file_path = changes['files'][0]['path']
            action = changes['files'][0]['type']
            return f"{action}: {file_path}"
        else:
            main_ext = max(file_types, key=file_types.get) if file_types else ""
            return f"Update {file_count} files ({main_ext} changes)"
    
    def create_branch(self, branch_name: str) -> Dict[str, Any]:
        """Create and switch to new branch"""
        success, stdout, stderr = self.run_git_command(['checkout', '-b', branch_name])
        
        return {
            'success': success,
            'message': stdout if success else stderr,
            'branch_name': branch_name
        }
    
    def switch_branch(self, branch_name: str) -> Dict[str, Any]:
        """Switch to existing branch"""
        success, stdout, stderr = self.run_git_command(['checkout', branch_name])
        
        return {
            'success': success,
            'message': stdout if success else stderr,
            'branch_name': branch_name
        }
    
    def get_diff(self, file_path: str = None) -> Dict[str, Any]:
        """Get diff for file or all changes"""
        args = ['diff', '--color=always']
        if file_path:
            args.append(file_path)
        
        success, stdout, stderr = self.run_git_command(args, capture_output=False)
        
        return {
            'success': success,
            'diff': stdout,
            'error': stderr if not success else None
        }
    
    def is_git_repository(self) -> bool:
        """Check if current directory is a git repository"""
        success, _, _ = self.run_git_command(['rev-parse', '--git-dir'])
        return success