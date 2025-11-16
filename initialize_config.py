# deepseek-code/initialize_config.py
#!/usr/bin/env python3
"""Quick configuration initialization script"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    print("🚀 Initializing DeepSeek-Code Configuration...")
    
    # Import after path setup
    from deepseek_code.cli.init_system import initialize_complete_system
    from deepseek_code.core.config_manager import ConfigManager
    
    # Initialize the complete system
    success = initialize_complete_system()
    
    if success:
        print("\n✅ Configuration files created successfully!")
        
        # Show where files are located
        config_manager = ConfigManager()
        config_dir = config_manager.config_dir
        
        print(f"\n📁 Configuration directory: {config_dir}")
        print("\n📄 Created files:")
        for file_path in config_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(config_dir)
                print(f"   - {relative_path}")
    else:
        print("\n❌ Failed to initialize configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()