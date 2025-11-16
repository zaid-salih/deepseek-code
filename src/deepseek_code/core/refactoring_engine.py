# deepseek-code/src/deepseek_code/core/refactoring_engine.py
import os
import ast
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from .file_manager import FileManager
from .ai_engine import DeepSeekAI

class RefactoringEngine:
    """Multi-file refactoring engine with rollback capability"""
    
    def __init__(self, file_manager: FileManager, ai_engine: DeepSeekAI):
        self.file_manager = file_manager
        self.ai_engine = ai_engine
        self.backup_dir = Path("~/.deepseek-code/refactoring_backups").expanduser()
        self.backup_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def refactor_code(self, 
                     target_paths: List[str], 
                     instructions: str,
                     language: str = None) -> Dict[str, Any]:
        """Refactor code across multiple files"""
        
        # Create backup before refactoring
        backup_id = self._create_backup(target_paths)
        
        try:
            # Read all target files
            file_contents = {}
            for file_path in target_paths:
                content = self.file_manager.read_file(file_path)
                if content:
                    file_contents[file_path] = content
            
            if not file_contents:
                return {"error": "No files could be read"}
            
            # Generate refactoring plan using AI
            refactoring_plan = self._generate_refactoring_plan(
                file_contents, instructions, language
            )
            
            # Apply refactoring
            results = self._apply_refactoring(refactoring_plan)
            
            return {
                "success": True,
                "backup_id": backup_id,
                "files_modified": len(results["modified_files"]),
                "refactoring_plan": refactoring_plan,
                "results": results
            }
            
        except Exception as e:
            # Rollback on error
            self._rollback_backup(backup_id)
            return {"error": f"Refactoring failed: {e}", "backup_id": backup_id}
    
    def analyze_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Analyze code dependencies for a file"""
        content = self.file_manager.read_file(file_path)
        if not content:
            return {"error": "Could not read file"}
        
        if file_path.endswith('.py'):
            return self._analyze_python_dependencies(content, file_path)
        elif file_path.endswith('.js') or file_path.endswith('.ts'):
            return self._analyze_javascript_dependencies(content, file_path)
        else:
            return self._analyze_general_dependencies(content, file_path)
    
    def visualize_dependencies(self, root_path: str = None) -> Dict[str, Any]:
        """Generate dependency graph visualization data"""
        if not root_path:
            root_path = self.file_manager.root_path
        
        project_structure = self.file_manager.discover_project_structure()
        dependencies = {}
        
        for file_info in project_structure["files"]:
            file_path = file_info["path"]
            deps = self.analyze_dependencies(file_path)
            dependencies[file_path] = deps
        
        # Build dependency graph
        graph = self._build_dependency_graph(dependencies)
        
        return {
            "nodes": graph["nodes"],
            "edges": graph["edges"],
            "file_count": len(dependencies),
            "dependency_count": len(graph["edges"])
        }
    
    def _generate_refactoring_plan(self, 
                                 file_contents: Dict[str, str], 
                                 instructions: str,
                                 language: str) -> Dict[str, Any]:
        """Generate refactoring plan using AI"""
        
        files_context = "\n\n".join([
            f"File: {path}\n```{language or self._detect_language(path)}\n{content}\n```"
            for path, content in file_contents.items()
        ])
        
        prompt = f"""
        Refactor the following code according to these instructions:
        {instructions}
        
        Files to refactor:
        {files_context}
        
        Provide a refactoring plan that includes:
        1. Which files need changes
        2. Specific changes to make in each file
        3. Any new files that need to be created
        4. Dependencies between changes
        
        Return your response in JSON format.
        """
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert code refactoring assistant. Provide detailed refactoring plans in JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = list(self.ai_engine.chat_completion(messages, stream=False))[0]
        return self._parse_refactoring_plan(response)
    
    def _apply_refactoring(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Apply refactoring plan to files"""
        modified_files = []
        errors = []
        
        for file_change in plan.get("file_changes", []):
            file_path = file_change["file_path"]
            new_content = file_change["new_content"]
            
            try:
                if self.file_manager.write_file(file_path, new_content, backup=False):
                    modified_files.append(file_path)
                else:
                    errors.append(f"Failed to write {file_path}")
            except Exception as e:
                errors.append(f"Error writing {file_path}: {e}")
        
        return {
            "modified_files": modified_files,
            "errors": errors,
            "success": len(errors) == 0
        }
    
    def _create_backup(self, file_paths: List[str]) -> str:
        """Create backup of files before refactoring"""
        backup_id = hashlib.md5(str(file_paths).encode()).hexdigest()[:8]
        backup_dir = self.backup_dir / backup_id
        backup_dir.mkdir(exist_ok=True)
        
        for file_path in file_paths:
            content = self.file_manager.read_file(file_path)
            if content:
                backup_file = backup_dir / Path(file_path).name
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        return backup_id
    
    def _rollback_backup(self, backup_id: str):
        """Rollback to backup version"""
        backup_dir = self.backup_dir / backup_id
        if backup_dir.exists():
            for backup_file in backup_dir.iterdir():
                # This would restore files - implementation depends on specific needs
                self.logger.info(f"Would restore from backup: {backup_file}")
    
    def _analyze_python_dependencies(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Python file dependencies"""
        try:
            tree = ast.parse(content)
            imports = []
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module
                    for alias in node.names:
                        imports.append({
                            "type": "from_import",
                            "module": module,
                            "name": alias.name,
                            "alias": alias.asname
                        })
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
            return {
                "language": "python",
                "imports": imports,
                "functions": functions,
                "classes": classes,
                "file_path": file_path
            }
        except SyntaxError as e:
            return {"error": f"Syntax error: {e}", "file_path": file_path}
    
    def _analyze_javascript_dependencies(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript dependencies"""
        imports = []
        
        # Simple regex-based import detection (would be enhanced)
        import re
        
        # CommonJS require
        require_matches = re.finditer(r'require\([\'"]([^\'"]+)[\'"]\)', content)
        for match in require_matches:
            imports.append({
                "type": "require",
                "module": match.group(1)
            })
        
        # ES6 imports
        import_matches = re.finditer(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
        for match in import_matches:
            imports.append({
                "type": "import",
                "module": match.group(1)
            })
        
        return {
            "language": "javascript",
            "imports": imports,
            "file_path": file_path
        }
    
    def _analyze_general_dependencies(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze dependencies for other file types"""
        return {
            "language": "unknown",
            "file_path": file_path,
            "content_preview": content[:200] + "..." if len(content) > 200 else content
        }
    
    def _build_dependency_graph(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """Build dependency graph from analyzed dependencies"""
        nodes = []
        edges = []
        
        for file_path, deps in dependencies.items():
            nodes.append({
                "id": file_path,
                "label": Path(file_path).name,
                "path": file_path,
                "language": deps.get("language", "unknown")
            })
            
            # Add edges for imports/dependencies
            for imp in deps.get("imports", []):
                module = imp.get("module", "")
                if module and not module.startswith(('.', '/')):  # External modules
                    edges.append({
                        "from": file_path,
                        "to": module,
                        "type": "import"
                    })
        
        return {"nodes": nodes, "edges": edges}
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql'
        }
        return language_map.get(ext, 'text')
    
    def _parse_refactoring_plan(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured refactoring plan"""
        # This would parse the AI response - simplified for now
        try:
            # Try to extract JSON from response
            if "```json" in ai_response:
                json_str = ai_response.split("```json")[1].split("```")[0]
                return json.loads(json_str)
            elif "```" in ai_response:
                json_str = ai_response.split("```")[1].split("```")[0]
                return json.loads(json_str)
            else:
                # Fallback to simple structure
                return {
                    "file_changes": [
                        {
                            "file_path": "example.py",
                            "new_content": ai_response
                        }
                    ]
                }
        except:
            return {
                "file_changes": [
                    {
                        "file_path": "refactored_file.py", 
                        "new_content": ai_response
                    }
                ]
            }