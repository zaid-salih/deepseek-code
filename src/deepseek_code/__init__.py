# deepseek-code/src/deepseek_code/__init__.py
"""DeepSeek-Code - AI-powered CLI IDE"""

__version__ = "1.0.0"
__author__ = "DeepSeek-Code Team"

from .core.ai_engine import DeepSeekAI
from .core.team_manager import TeamManager
from .core.file_manager import FileManager
from .cli.terminal_ui import TerminalUI