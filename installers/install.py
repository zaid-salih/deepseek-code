# deepseek-code/installers/install.py
#!/usr/bin/env python3
"""Cross-platform installer for DeepSeek-Code"""

import os
import sys
import platform
import subprocess
import urllib.request
import zipfile
import tarfile
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command with error handling"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def install_windows():
    """Windows installation"""
    print("🚀 Installing DeepSeek-Code on Windows...")
    
    # Check if Python is installed
    success, stdout, stderr = run_command("python --version")
    if not success:
        print("❌ Python not found. Please install Python 3.9+ first.")
        return False
    
    # Create virtual environment
    print("📦 Creating virtual environment...")
    venv_path = Path.home() / ".deepseek-code" / "venv"
    success, stdout, stderr = run_command(f"python -m venv {venv_path}")
    if not success:
        print(f"❌ Failed to create virtual environment: {stderr}")
        return False
    
    # Install package
    pip_path = venv_path / "Scripts" / "pip.exe"
    success, stdout, stderr = run_command(f'{pip_path} install "deepseek-code @ git+https://github.com/yourusername/deepseek-code.git"')
    if not success:
        print(f"❌ Failed to install DeepSeek-Code: {stderr}")
        return False
    
    # Add to PATH (user level)
    bin_path = venv_path / "Scripts"
    success, stdout, stderr = run_command(f'setx PATH "%PATH%;{bin_path}"')
    if success:
        print("✅ Added to PATH")
    else:
        print("⚠️  Could not add to PATH automatically. Please add manually:")
        print(f"   {bin_path}")
    
    return True

def install_linux_macos():
    """Linux/macOS installation"""
    print("🚀 Installing DeepSeek-Code on Linux/macOS...")
    
    # Check if Python is installed
    success, stdout, stderr = run_command("python3 --version")
    if not success:
        print("❌ Python 3 not found. Please install Python 3.9+ first.")
        return False
    
    # Create virtual environment
    print("📦 Creating virtual environment...")
    venv_path = Path.home() / ".deepseek-code" / "venv"
    success, stdout, stderr = run_command(f"python3 -m venv {venv_path}")
    if not success:
        print(f"❌ Failed to create virtual environment: {stderr}")
        return False
    
    # Install package
    pip_path = venv_path / "bin" / "pip"
    success, stdout, stderr = run_command(f'{pip_path} install "deepseek-code @ git+https://github.com/yourusername/deepseek-code.git"')
    if not success:
        print(f"❌ Failed to install DeepSeek-Code: {stderr}")
        return False
    
    # Add to bashrc/zshrc
    bin_path = venv_path / "bin"
    shell_rc = Path.home() / (".zshrc" if "zsh" in os.environ.get("SHELL", "") else ".bashrc")
    
    export_line = f'\nexport PATH="{bin_path}:$PATH"\n'
    try:
        with open(shell_rc, 'a') as f:
            f.write(export_line)
        print(f"✅ Added to {shell_rc}")
    except Exception as e:
        print(f"⚠️  Could not update shell rc file: {e}")
        print("Please add manually:")
        print(f'export PATH="{bin_path}:$PATH"')
    
    return True

def main():
    """Main installation function"""
    system = platform.system().lower()
    
    print("🎯 DeepSeek-Code Installation")
    print("=" * 50)
    
    if system == "windows":
        success = install_windows()
    elif system in ["linux", "darwin"]:  # darwin is macOS
        success = install_linux_macos()
    else:
        print(f"❌ Unsupported platform: {system}")
        return
    
    if success:
        print("\n✅ Installation complete!")
        print("\nNext steps:")
        print("1. Restart your terminal")
        print("2. Run: deepseek-code setup")
        print("3. Follow the setup wizard")
        print("\nFor help: deepseek-code --help")
    else:
        print("\n❌ Installation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()