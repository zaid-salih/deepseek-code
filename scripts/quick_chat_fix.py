# deepseek-code/quick_chat_fix.py
#!/usr/bin/env python3
"""Quick fix for chat streaming"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def quick_fix_chat():
    """Apply a quick fix to the chat function"""
    file_path = "src/deepseek_code/cli/final_main.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the streaming section with a buffered approach
    old_code = '''            # Display AI response with streaming
            ui.console.print()
            with ui.console.status("[bold green]Thinking...[/bold green]"):
                try:
                    response_text = ""
                    for chunk in ai_engine.chat_completion(
                        conversation_history[-10:],
                        stream=True
                    ):
                        response_text += chunk
                        # Print each chunk as it comes
                        ui.console.print(chunk, end="")
                    
                    # Ensure final newline and display the complete response
                    ui.console.print()
                    ui.console.print()'''
    
    new_code = '''            # Display AI response with buffered streaming
            ui.console.print()
            ui.console.print("[bold green]🤖 DeepSeek:[/bold green]")
            
            try:
                # First collect all chunks
                with ui.console.status("[bold green]Thinking...[/bold green]"):
                    chunks = []
                    for chunk in ai_engine.chat_completion(
                        conversation_history[-10:],
                        stream=True
                    ):
                        chunks.append(chunk)
                
                # Then display the complete response
                response_text = "".join(chunks)
                ui.console.print(response_text)
                ui.console.print()'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Applied quick chat fix!")
        return True
    else:
        print("❌ Could not find the code to replace")
        return False

if __name__ == "__main__":
    quick_fix_chat()