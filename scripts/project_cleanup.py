# deepseek-code/project_cleanup.py
#!/usr/bin/env python3
"""Clean up and organize the DeepSeek-Code project"""

import os
import shutil
from pathlib import Path

def analyze_project_structure():
    """Analyze current project structure"""
    print("📊 Analyzing Project Structure...")
    print("=" * 50)
    
    file_types = {}
    total_size = 0
    
    for file_path in Path('.').rglob('*'):
        if file_path.is_file():
            # Skip .git directory
            if '.git' in file_path.parts:
                continue
                
            ext = file_path.suffix.lower() or 'no extension'
            file_types[ext] = file_types.get(ext, 0) + 1
            total_size += file_path.stat().st_size
    
    print(f"📁 Total files: {sum(file_types.values())}")
    print(f"💾 Total size: {total_size / 1024 / 1024:.2f} MB")
    print("\n📄 File types:")
    for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {ext:15} {count:4} files")
    
    return file_types, total_size

def create_cleanup_plan():
    """Create a cleanup plan"""
    print("\n🎯 Cleanup Plan")
    print("=" * 50)
    
    plan = {
        'keep': {
            'description': 'Essential project files',
            'files': [
                # Source code
                'src/deepseek_code/',
                'vscode_extension/',
                'visualstudio_extension/',
                
                # Configuration
                'pyproject.toml',
                'requirements.txt',
                'README.md',
                
                # Installers
                'installers/',
            ]
        },
        'organize': {
            'description': 'Move to organized directories',
            'files': {
                'scripts/': [
                    'fix_*.py',
                    'cleanup_*.py', 
                    'test_*.py',
                    'setup_*.py',
                    'final_*.py',
                    'ultimate_*.py',
                    'minimal_*.py',
                    'safe_*.py',
                    'quick_*.py',
                    'debug_*.py',
                    'basic_test.py',
                    'comprehensive_fix.py',
                    'final_verification.py',
                ],
                'examples/': [
                    'test_file.py',
                    'your_file.py',
                ],
                'docs/': [
                    '*.md',
                    '*.txt',
                ]
            }
        },
        'remove': {
            'description': 'Temporary files to remove',
            'patterns': [
                'delete.me',
                '*.pyc',
                '__pycache__/',
                '*.egg-info/',
                '.pytest_cache/',
                '.coverage',
                'htmlcov/',
                '.mypy_cache/',
            ]
        }
    }
    
    print("✅ Keep: Essential project structure")
    for item in plan['keep']['files']:
        print(f"   📁 {item}")
    
    print("\n📂 Organize: Move to proper directories")
    for dest_dir, patterns in plan['organize']['files'].items():
        print(f"   📁 {dest_dir}")
        for pattern in patterns:
            print(f"     └── {pattern}")
    
    print("\n🗑️  Remove: Temporary files")
    for pattern in plan['remove']['patterns']:
        print(f"   ❌ {pattern}")
    
    return plan

def create_organized_structure():
    """Create organized directory structure"""
    print("\n🏗️ Creating organized structure...")
    
    directories = [
        'scripts/',
        'examples/', 
        'docs/',
        'tests/',
        'backups/'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   📁 Created: {directory}")

def move_script_files():
    """Move script files to scripts directory"""
    print("\n📦 Organizing script files...")
    
    script_patterns = [
        'fix_*.py',
        'cleanup_*.py',
        'test_*.py', 
        'setup_*.py',
        'final_*.py',
        'ultimate_*.py',
        'minimal_*.py',
        'safe_*.py',
        'quick_*.py',
        'debug_*.py',
        'basic_test.py',
        'comprehensive_fix.py',
        'final_verification.py',
        'project_cleanup.py',  # This file itself
    ]
    
    moved_count = 0
    for pattern in script_patterns:
        for file_path in Path('.').glob(pattern):
            if file_path.name != 'project_cleanup.py':  # Don't move current file yet
                try:
                    shutil.move(str(file_path), f'scripts/{file_path.name}')
                    print(f"   📄 Moved: {file_path.name} → scripts/")
                    moved_count += 1
                except Exception as e:
                    print(f"   ⚠️  Could not move {file_path.name}: {e}")
    
    return moved_count

def move_example_files():
    """Move example files to examples directory"""
    print("\n📝 Organizing example files...")
    
    example_files = [
        'test_file.py',
        'your_file.py',
    ]
    
    moved_count = 0
    for filename in example_files:
        file_path = Path(filename)
        if file_path.exists():
            try:
                shutil.move(str(file_path), f'examples/{file_path.name}')
                print(f"   📄 Moved: {file_path.name} → examples/")
                moved_count += 1
            except Exception as e:
                print(f"   ⚠️  Could not move {file_path.name}: {e}")
    
    return moved_count

def remove_temporary_files():
    """Remove temporary files and directories"""
    print("\n🗑️  Cleaning temporary files...")
    
    remove_patterns = [
        'delete.me',
        '*.pyc',
        '__pycache__',
        '*.egg-info',
        '.pytest_cache',
        '.coverage',
        'htmlcov',
        '.mypy_cache',
    ]
    
    removed_count = 0
    for pattern in remove_patterns:
        for file_path in Path('.').rglob(pattern):
            try:
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                    print(f"   📁 Removed: {file_path}/")
                else:
                    file_path.unlink()
                    print(f"   📄 Removed: {file_path.name}")
                removed_count += 1
            except Exception as e:
                print(f"   ⚠️  Could not remove {file_path}: {e}")
    
    return removed_count

def create_final_structure():
    """Create the final organized structure"""
    print("\n🎯 Final Project Structure")
    print("=" * 50)
    
    final_structure = """
deepseek-code/
├── 📁 src/                          # Main source code
│   └── deepseek_code/
│       ├── cli/                     # CLI commands
│       ├── core/                    # Core functionality  
│       └── ide/                     # IDE integration
├── 📁 vscode_extension/             # VS Code extension
├── 📁 visualstudio_extension/       # Visual Studio extension
├── 📁 installers/                   # Installation scripts
├── 📁 scripts/                      # Development & utility scripts
├── 📁 examples/                     # Example files and tests
├── 📁 docs/                         # Documentation
├── 📄 pyproject.toml               # Project configuration
├── 📄 requirements.txt              # Dependencies
└── 📄 README.md                     # Project documentation
"""
    
    print(final_structure)

def create_usage_guide():
    """Create a usage guide after cleanup"""
    print("\n📖 Usage Guide After Cleanup")
    print("=" * 50)
    
    guide = """
🚀 **Using DeepSeek-Code After Cleanup:**

**Essential Commands:**
python -m deepseek_code.cli.improved_chat      # Best chat experience
python -m deepseek_code.cli.ultimate_main      # All features

**Development & Testing:**
cd scripts/
python final_verification.py                   # Verify system
python basic_test.py                          # Quick test

**Project Structure:**
- src/              - Main source code
- scripts/          - Utility and test scripts  
- examples/         - Example files
- installers/       - Installation scripts
- docs/             - Documentation

**Main Entry Points:**
- improved_chat.py  - Optimized chat interface
- ultimate_main.py  - Complete feature set
- final_main.py     - Original main (fixed)
"""
    
    print(guide)

def main():
    """Main cleanup function"""
    print("🧹 DeepSeek-Code Project Cleanup")
    print("=" * 60)
    
    # Analyze current structure
    file_types, total_size = analyze_project_structure()
    
    # Create cleanup plan
    plan = create_cleanup_plan()
    
    # Get user confirmation
    print("\n⚠️  This will reorganize your project files.")
    response = input("Proceed with cleanup? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("Cleanup cancelled.")
        return
    
    # Execute cleanup
    create_organized_structure()
    
    moved_scripts = move_script_files()
    moved_examples = move_example_files() 
    removed_temp = remove_temporary_files()
    
    # Move this cleanup script last
    try:
        shutil.move('project_cleanup.py', 'scripts/project_cleanup.py')
        print("   📄 Moved: project_cleanup.py → scripts/")
    except:
        pass
    
    # Show results
    print("\n📊 Cleanup Results:")
    print("=" * 50)
    print(f"✅ Scripts organized: {moved_scripts} files")
    print(f"✅ Examples organized: {moved_examples} files") 
    print(f"✅ Temporary files removed: {removed_temp} items")
    
    # Show final structure
    create_final_structure()
    create_usage_guide()
    
    print("\n🎉 Project cleanup completed!")
    print("💡 Your project is now organized and ready for development.")

if __name__ == "__main__":
    main()