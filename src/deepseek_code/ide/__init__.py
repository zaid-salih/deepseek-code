# deepseek-code/src/deepseek_code/ide/__init__.py
"""IDE Integration modules for DeepSeek-Code"""

from .lsp_server import DeepSeekLanguageServer, start_lsp_server

__all__ = ['DeepSeekLanguageServer', 'start_lsp_server']