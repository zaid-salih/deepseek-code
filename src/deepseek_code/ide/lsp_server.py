# deepseek-code/src/deepseek_code/ide/lsp_server.py
import asyncio
import json
import logging
from typing import Optional, List, Dict, Any
from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_REFERENCES,
    CompletionOptions,
    CompletionParams,
    CompletionList,
    CompletionItem,
    Hover,
    Position,
    Range,
    Location,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
)
from lsprotocol.types import (
    InitializeParams,
    InitializeResult,
    ServerCapabilities,
    TextDocumentSyncKind,
)

from ..core.ai_engine import DeepSeekAI
from ..core.team_manager import TeamManager

class DeepSeekLanguageServer(LanguageServer):
    def __init__(self):
        super().__init__("deepseek-code-lsp", "1.0.0")
        
        self.ai_engine: Optional[DeepSeekAI] = None
        self.team_manager = TeamManager()
        self.document_contents: Dict[str, str] = {}
        
        self.initialize_ai_engine()
        
    def initialize_ai_engine(self):
        """Initialize the AI engine with team configuration"""
        try:
            team_config = self.team_manager._load_team_config()
            if team_config and team_config.get("api_key"):
                api_key = self.team_manager.decrypt_api_key(team_config["api_key"])
                self.ai_engine = DeepSeekAI(api_key)
                self.show_message_log("DeepSeek AI engine initialized successfully")
            else:
                self.show_message_log("DeepSeek API key not configured. Some features may not work.")
        except Exception as e:
            self.show_message_log(f"Failed to initialize AI engine: {e}")
    
    def show_message_log(self, message: str, message_type: int = 3):  # 3 = Log
        """Show message in client's log"""
        self.show_message(message, msg_type=message_type)

server = DeepSeekLanguageServer()

@server.feature(INITIALIZE)
def initialize(params: InitializeParams) -> InitializeResult:
    """Initialize the language server"""
    server.show_message_log("DeepSeek-Code Language Server initializing...")
    
    return InitializeResult(
        capabilities=ServerCapabilities(
            text_document_sync=TextDocumentSyncKind.INCREMENTAL,
            completion_provider=CompletionOptions(
                trigger_characters=[".", " ", "#", "//"],
                resolve_provider=False
            ),
            hover_provider=True,
            definition_provider=True,
            references_provider=True,
        )
    )

@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(params: DidOpenTextDocumentParams):
    """Handle document open event"""
    document_uri = params.text_document.uri
    document_text = server.document_contents.get(document_uri, "")
    server.show_message_log(f"Document opened: {document_uri}")

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(params: DidChangeTextDocumentParams):
    """Handle document change event"""
    document_uri = params.text_document.uri
    for change in params.content_changes:
        server.document_contents[document_uri] = change.text

@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(params: CompletionParams) -> Optional[CompletionList]:
    """Provide code completions using AI"""
    if not server.ai_engine:
        return None
    
    document_uri = params.text_document.uri
    position = params.position
    document_text = server.document_contents.get(document_uri, "")
    
    # Get current line and context
    lines = document_text.split('\n')
    if position.line >= len(lines):
        return None
    
    current_line = lines[position.line]
    line_prefix = current_line[:position.character]
    
    # Only provide AI completions in specific contexts
    if not should_provide_ai_completion(line_prefix):
        return None
    
    try:
        # Use AI to generate completion suggestions
        context = get_context_around_position(document_text, position)
        completion = get_ai_completion(server.ai_engine, context, line_prefix)
        
        if completion:
            return CompletionList(
                is_incomplete=False,
                items=[
                    CompletionItem(
                        label=completion,
                        detail="DeepSeek AI Suggestion",
                        documentation=completion,
                        insert_text=completion
                    )
                ]
            )
    
    except Exception as e:
        server.show_message_log(f"Completion error: {e}")
    
    return None

@server.feature(TEXT_DOCUMENT_HOVER)
def hover(params: CompletionParams) -> Optional[Hover]:
    """Provide hover information using AI"""
    if not server.ai_engine:
        return None
    
    document_uri = params.text_document.uri
    position = params.position
    document_text = server.document_contents.get(document_uri, "")
    
    # Get word at position
    lines = document_text.split('\n')
    if position.line >= len(lines):
        return None
    
    current_line = lines[position.line]
    word = get_word_at_position(current_line, position.character)
    
    if not word:
        return None
    
    try:
        # Use AI to explain the code element
        context = get_context_around_position(document_text, position)
        explanation = get_ai_explanation(server.ai_engine, word, context)
        
        if explanation:
            return Hover(
                contents=explanation,
                range=Range(
                    start=Position(line=position.line, character=position.character - len(word)),
                    end=Position(line=position.line, character=position.character)
                )
            )
    
    except Exception as e:
        server.show_message_log(f"Hover error: {e}")
    
    return None

@server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(params: CompletionParams) -> Optional[List[Location]]:
    #"""Provide definition locations (simplified)"""
    # This would be enhanced with proper symbol analysis
    return None

@server.feature(TEXT_DOCUMENT_REFERENCES)
def references(params: CompletionParams) -> Optional[List[Location]]:
    #"""Provide reference locations (simplified)"""
    # This would be enhanced with proper symbol analysis
    return None

def should_provide_ai_completion(line_prefix: str) -> bool:
    #"""Determine if AI completion should be provided"""
    triggers = [
        "# ", "// ", "def ", "function ", "class ", "if ", "for ", "while ",
        "const ", "let ", "var ", "public ", "private ", "protected "
    ]
    
    return any(line_prefix.endswith(trigger) for trigger in triggers)

def get_context_around_position(document_text: str, position: Position, lines_before: int = 5, lines_after: int = 2) -> str:
    #"""Get context around the current position"""
    lines = document_text.split('\n')
    start_line = max(0, position.line - lines_before)
    end_line = min(len(lines), position.line + lines_after + 1)
    
    context_lines = lines[start_line:end_line]
    return '\n'.join(context_lines)

def get_word_at_position(line: str, position: int) -> Optional[str]:
    #"""Get the word at the given position in the line"""
    if position >= len(line) or position < 0:
        return None
    
    # Find word boundaries
    start = position
    while start > 0 and (line[start-1].isalnum() or line[start-1] == '_'):
        start -= 1
    
    end = position
    while end < len(line) and (line[end].isalnum() or line[end] == '_'):
        end += 1
    
    word = line[start:end]
    return word if word.strip() else None

def get_ai_completion(ai_engine: DeepSeekAI, context: str, prefix: str) -> Optional[str]:
    #"""Get AI-powered completion suggestion"""
    messages = [
        {
            "role": "system",
            "content": """You are a code completion assistant. Provide only the completion text without explanations.
            Complete the code based on the context and prefix. Return only the completion text."""
        },
        {
            "role": "user",
            "content": f"""Context:
            ```python
            {context}
            Complete this: {prefix}"""
        }
        ]   
    try:
        response = list(ai_engine.chat_completion(messages, stream=False))[0]
        # Extract just the completion part
        completion = response.strip()
        if completion.startswith(prefix):
            completion = completion[len(prefix):]
        return completion
    except Exception:
        return None

#"""Get AI-powered explanation for a code element"""
def get_ai_explanation(ai_engine: DeepSeekAI, word: str, context: str) -> Optional[str]:
    messages = [
        {
            "role": "system",
            "content": "You are a code explanation assistant. Provide concise explanations of code elements."
        },
        {
            "role": "user",
            "content": f"""In this code context:
            {context}
            What is '{word}'? Provide a brief explanation."""
        }
        ]
    try:
        response = list(ai_engine.chat_completion(messages, stream=False))[0]
        return response.strip()
    except Exception:
        return None

#"""Start the LSP server"""
def start_lsp_server():
    try:
        server.start_io()
    except Exception as e:
        logging.error(f"LSP server error: {e}")

if name == "main":
    start_lsp_server()