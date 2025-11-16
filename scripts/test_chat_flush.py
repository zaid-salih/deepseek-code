# deepseek-code/test_chat_flush.py
#!/usr/bin/env python3
"""Test chat with forced flushing"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepseek_code.core.ai_engine import DeepSeekAI
from deepseek_code.core.team_manager import TeamManager
from deepseek_code.core.file_manager import FileManager
from deepseek_code.cli.terminal_ui import TerminalUI

def test_chat_with_flush():
    """Test chat with proper flushing"""
    team_manager = TeamManager()
    team_config = team_manager._load_team_config()
    
    if not team_config:
        print("❌ Team configuration not found")
        return
    
    try:
        api_key = team_manager.decrypt_api_key(team_config["api_key"])
        ai_engine = DeepSeekAI(api_key)
    except Exception as e:
        print(f"❌ API key issue: {e}")
        return
    
    ui = TerminalUI()
    ui.display_welcome()
    
    conversation_history = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Keep responses concise."
        }
    ]
    
    print("💬 Test Chat (with flushing)")
    print("Type 'quit' to exit")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            conversation_history.append({"role": "user", "content": user_input})
            
            print("\nAI: ", end="", flush=True)
            
            try:
                # Collect and display with flushing
                response_text = ""
                for chunk in ai_engine.chat_completion(conversation_history[-5:], stream=True):
                    response_text += chunk
                    print(chunk, end="", flush=True)  # Force flush after each chunk
                
                print()  # Final newline
                
                conversation_history.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            break

if __name__ == "__main__":
    test_chat_with_flush()