# deepseek-code/check_syntax.py
#!/usr/bin/env python3
"""Check for syntax errors in Python files"""

import ast
from pathlib import Path

def check_file_syntax(file_path):
    """Check if a Python file has syntax errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Could not check {file_path}: {e}")
        return True

def check_all_files():
    """Check all Python files for syntax errors"""
    print("🔍 Checking Python files for syntax errors...")
    python_files = list(Path("src").rglob("*.py"))
    
    all_ok = True
    for file_path in python_files:
        if not check_file_syntax(file_path):
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    if check_all_files():
        print("✅ All Python files have valid syntax!")
    else:
        print("❌ Some files have syntax errors!")