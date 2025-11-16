# deepseek-code/fix_imports.py
#!/usr/bin/env python3
"""Fix import issues in the codebase"""

import os
import re
from pathlib import Path

def fix_git_integration_imports():
    """Fix missing imports in git_integration.py"""
    file_path = Path("src/deepseek_code/core/git_integration.py")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if Any is already imported
        if "from typing import" in content and "Any" in content:
            print("✅ Any import already exists in git_integration.py")
            return True
        
        # Fix the typing import
        if "from typing import" in content:
            # Add Any to existing import
            content = content.replace(
                "from typing import Dict, List, Optional, Tuple",
                "from typing import Dict, List, Optional, Tuple, Any"
            )
        else:
            # Add the import at the top
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('import') or line.startswith('from'):
                    continue
                if line.strip() and not line.startswith('#'):
                    # Insert after existing imports
                    lines.insert(i, "from typing import Dict, List, Optional, Tuple, Any")
                    break
            content = '\n'.join(lines)
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed imports in git_integration.py")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix imports: {e}")
        return False

def fix_all_imports():
    """Fix imports in all core files"""
    files_to_check = [
        "src/deepseek_code/core/git_integration.py",
        "src/deepseek_code/core/refactoring_engine.py", 
        "src/deepseek_code/core/testing_integration.py",
        "src/deepseek_code/core/code_review.py",
        "src/deepseek_code/core/analytics.py",
        "src/deepseek_code/core/project_templates.py"
    ]
    
    success_count = 0
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if Any is used but not imported
                if "-> Dict[str, Any]" in content or "-> List[Any]" in content:
                    if "from typing import Any" not in content and "from typing import" in content:
                        # Add Any to existing import
                        content = content.replace(
                            "from typing import Dict, List, Optional, Tuple",
                            "from typing import Dict, List, Optional, Tuple, Any"
                        )
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"✅ Fixed imports in {path.name}")
                        success_count += 1
                    else:
                        print(f"✅ {path.name} already has correct imports")
                else:
                    print(f"✅ {path.name} doesn't use Any type")
            except Exception as e:
                print(f"❌ Failed to fix {path.name}: {e}")
        else:
            print(f"⚠️  File not found: {path}")
    
    return success_count > 0

def main():
    print("🔧 Fixing Import Issues")
    print("=" * 40)
    
    # Fix the main culprit first
    if fix_git_integration_imports():
        print("\n✅ Main import fix applied!")
    else:
        print("\n❌ Failed to fix main imports")
        return False
    
    # Fix any other files
    print("\n🔍 Checking other files...")
    fix_all_imports()
    
    print("\n🎯 Testing the fix...")
    return test_fix()

def test_fix():
    """Test if the import fix worked"""
    try:
        from src.deepseek_code.core.git_integration import GitIntegration
        print("✅ git_integration.py imports correctly!")
        return True
    except ImportError as e:
        print(f"❌ Still having import issues: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Imports fixed! You can now run the system.")
        print("\nTry: python -m deepseek_code.cli.main --help")
    else:
        print("\n❌ Failed to fix imports. Manual intervention needed.")