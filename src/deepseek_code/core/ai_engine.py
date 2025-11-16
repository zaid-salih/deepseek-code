# deepseek-code/src/deepseek_code/core/ai_engine.py
import os
import json
import requests
from typing import Dict, List, Any, Generator
import logging

class DeepSeekAI:
    """DeepSeek API integration engine"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        self.logger = logging.getLogger(__name__)
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: str = "deepseek-coder",
                       stream: bool = False,
                       **kwargs) -> Generator[str, None, None]:
        """Send chat completion request to DeepSeek API"""
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data != '[DONE]':
                                try:
                                    chunk = json.loads(data)
                                    if 'choices' in chunk and chunk['choices']:
                                        delta = chunk['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            yield delta['content']
                                except json.JSONDecodeError:
                                    continue
            else:
                data = response.json()
                yield data['choices'][0]['message']['content']
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise
    
    def analyze_code(self, code: str, language: str = None) -> Dict[str, Any]:
        """Analyze code and provide insights"""
        messages = [
            {
                "role": "system",
                "content": "You are an expert code analyzer. Provide detailed analysis of the given code including complexity, potential issues, and improvements."
            },
            {
                "role": "user", 
                "content": f"Analyze this {language + ' ' if language else ''}code:\n```\n{code}\n```"
            }
        ]
        
        response = list(self.chat_completion(messages, stream=False))[0]
        return {
            "analysis": response,
            "language": language or "unknown"
        }
    
    def refactor_code(self, code: str, instructions: str, language: str) -> str:
        """Refactor code based on instructions"""
        messages = [
            {
                "role": "system",
                "content": f"You are a {language} refactoring expert. Refactor the code according to the instructions while maintaining functionality."
            },
            {
                "role": "user",
                "content": f"Original code:\n```{language}\n{code}\n```\n\nInstructions: {instructions}\n\nRefactored code:"
            }
        ]
        
        response = list(self.chat_completion(messages, stream=False))[0]
        return self._extract_code_from_response(response, language)
    
    def _extract_code_from_response(self, response: str, language: str) -> str:
        """Extract code from AI response"""
        # Look for code blocks
        if f"```{language}" in response:
            start = response.find(f"```{language}") + len(f"```{language}\n")
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        else:
            return response.strip()