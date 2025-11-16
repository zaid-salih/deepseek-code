# deepseek-code/src/deepseek_code/core/testing_integration.py
import os
import subprocess
import glob
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

class TestingIntegration:
    """Testing framework detection and integration"""
    
    def __init__(self, root_path: str = None):
        self.root_path = Path(root_path or os.getcwd())
        self.logger = logging.getLogger(__name__)
    
    def detect_testing_frameworks(self) -> Dict[str, Any]:
        """Detect testing frameworks in project"""
        frameworks = {}
        
        # Check for Python testing frameworks
        if self._has_file('pytest.ini') or self._has_file('pyproject.toml'):
            frameworks['pytest'] = self._detect_pytest_config()
        
        if self._has_file('setup.py') or self._has_file('requirements.txt'):
            if self._has_module('unittest'):
                frameworks['unittest'] = self._detect_unittest_config()
        
        # Check for JavaScript testing frameworks
        if self._has_file('package.json'):
            frameworks.update(self._detect_js_testing_frameworks())
        
        # Check for other languages
        if self._has_file('Makefile'):
            frameworks['make'] = self._detect_makefile_tests()
        
        return frameworks
    
    def run_tests(self, 
                 framework: str = 'auto',
                 test_path: str = None,
                 args: List[str] = None) -> Dict[str, Any]:
        """Run tests using detected framework"""
        if framework == 'auto':
            frameworks = self.detect_testing_frameworks()
            framework = next(iter(frameworks.keys()), 'pytest')
        
        test_args = args or []
        
        if framework == 'pytest':
            return self._run_pytest_tests(test_path, test_args)
        elif framework == 'unittest':
            return self._run_unittest_tests(test_path, test_args)
        elif framework == 'jest':
            return self._run_jest_tests(test_path, test_args)
        elif framework == 'mocha':
            return self._run_mocha_tests(test_path, test_args)
        else:
            return {"error": f"Unsupported testing framework: {framework}"}
    
    def generate_test(self, 
                     file_path: str, 
                     framework: str = 'auto') -> Dict[str, Any]:
        """Generate tests for a file using AI"""
        content = self._read_file(file_path)
        if not content:
            return {"error": f"Could not read file: {file_path}"}
        
        # Detect framework from file
        if framework == 'auto':
            framework = self._detect_framework_from_file(file_path)
        
        prompt = f"""
        Generate comprehensive tests for the following {framework} code:
        
        File: {file_path}
        Code:
        ```{self._get_language_from_path(file_path)}
        {content}
        ```
        
        Please provide complete test coverage including:
        - Unit tests for all functions/methods
        - Edge cases and error conditions
        - Mocking where appropriate
        - Clear test descriptions
        
        Return the test code in a separate file with appropriate naming.
        """
        
        # This would integrate with AI engine
        return {
            "framework": framework,
            "original_file": file_path,
            "test_file": f"test_{Path(file_path).name}",
            "prompt": prompt
        }
    
    def _run_pytest_tests(self, test_path: str, args: List[str]) -> Dict[str, Any]:
        """Run pytest tests"""
        cmd = ['pytest']
        if test_path:
            cmd.append(test_path)
        cmd.extend(args)
        
        return self._run_command(cmd, "pytest")
    
    def _run_unittest_tests(self, test_path: str, args: List[str]) -> Dict[str, Any]:
        """Run unittest tests"""
        cmd = ['python', '-m', 'unittest']
        if test_path:
            cmd.append(test_path)
        cmd.extend(args)
        
        return self._run_command(cmd, "unittest")
    
    def _run_jest_tests(self, test_path: str, args: List[str]) -> Dict[str, Any]:
        """Run Jest tests"""
        cmd = ['npx', 'jest']
        if test_path:
            cmd.append(test_path)
        cmd.extend(args)
        
        return self._run_command(cmd, "jest")
    
    def _run_mocha_tests(self, test_path: str, args: List[str]) -> Dict[str, Any]:
        """Run Mocha tests"""
        cmd = ['npx', 'mocha']
        if test_path:
            cmd.append(test_path)
        cmd.extend(args)
        
        return self._run_command(cmd, "mocha")
    
    def _run_command(self, cmd: List[str], framework: str) -> Dict[str, Any]:
        """Run a command and capture results"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "framework": framework,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": " ".join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                "framework": framework,
                "success": False,
                "error": "Test execution timed out",
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "framework": framework,
                "success": False,
                "error": str(e),
                "command": " ".join(cmd)
            }
    
    def _detect_pytest_config(self) -> Dict[str, Any]:
        """Detect pytest configuration"""
        config = {"detected": True}
        
        if self._has_file('pytest.ini'):
            config['config_file'] = 'pytest.ini'
        elif self._has_file('pyproject.toml'):
            config['config_file'] = 'pyproject.toml'
        
        # Find test files
        test_files = glob.glob(str(self.root_path / '**' / 'test_*.py'), recursive=True)
        test_files.extend(glob.glob(str(self.root_path / '**' / '*_test.py'), recursive=True))
        
        config['test_files'] = [Path(f).name for f in test_files[:10]]  # First 10
        config['test_file_count'] = len(test_files)
        
        return config
    
    def _detect_unittest_config(self) -> Dict[str, Any]:
        """Detect unittest configuration"""
        test_files = glob.glob(str(self.root_path / '**' / 'test_*.py'), recursive=True)
        
        return {
            "detected": True,
            "test_files": [Path(f).name for f in test_files[:10]],
            "test_file_count": len(test_files)
        }
    
    def _detect_js_testing_frameworks(self) -> Dict[str, Any]:
        """Detect JavaScript testing frameworks"""
        frameworks = {}
        
        package_json = self._read_json_file('package.json')
        if package_json:
            scripts = package_json.get('scripts', {})
            dependencies = {**package_json.get('dependencies', {}), 
                          **package_json.get('devDependencies', {})}
            
            if 'jest' in str(scripts) or any('jest' in key for key in dependencies.keys()):
                frameworks['jest'] = {"detected": True}
            
            if 'mocha' in str(scripts) or any('mocha' in key for key in dependencies.keys()):
                frameworks['mocha'] = {"detected": True}
        
        return frameworks
    
    def _detect_makefile_tests(self) -> Dict[str, Any]:
        """Detect tests in Makefile"""
        makefile_content = self._read_file('Makefile')
        if makefile_content and 'test:' in makefile_content:
            return {"detected": True, "target": "test"}
        return {"detected": False}
    
    def _has_file(self, filename: str) -> bool:
        """Check if file exists in project"""
        return (self.root_path / filename).exists()
    
    def _has_module(self, module_name: str) -> bool:
        """Check if Python module is available"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def _read_file(self, filename: str) -> Optional[str]:
        """Read file content"""
        try:
            with open(self.root_path / filename, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    
    def _read_json_file(self, filename: str) -> Optional[Dict]:
        """Read and parse JSON file"""
        content = self._read_file(filename)
        if content:
            try:
                import json
                return json.loads(content)
            except:
                pass
        return None
    
    def _detect_framework_from_file(self, file_path: str) -> str:
        """Detect testing framework from file path"""
        if file_path.endswith('.py'):
            return 'pytest'
        elif file_path.endswith('.js') or file_path.endswith('.ts'):
            return 'jest'
        else:
            return 'pytest'  # Default
    
    def _get_language_from_path(self, file_path: str) -> str:
        """Get language from file extension"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c'
        }
        return language_map.get(ext, 'text')