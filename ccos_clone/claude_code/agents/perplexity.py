"""
Perplexity AI API integration with local context awareness.
"""

import httpx
import json
import os
import glob
from typing import Dict, List, Tuple

# Try to get API key from environment variable first
API_KEY = os.getenv("PPLX_API_KEY", "")

class PerplexityAPI:
    def __init__(self):
        if not API_KEY:
            raise ValueError("Perplexity API key not found. Please set PPLX_API_KEY environment variable.")
            
        self.base_url = "https://api.perplexity.ai"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        # Local command handlers
        self.commands = {
            "help": self._handle_help,
            "exit": self._handle_exit,
            "quit": self._handle_exit,
            "ls": self._handle_ls,
        }
        
    def _handle_help(self) -> str:
        """Handle help command."""
        return """Available commands:
• help - Show this help message
• exit/quit - Exit the application
• ls - List files in current directory

For all other queries:
• Ask about code in any file
• Request code explanations
• Get code analysis
• Ask to see specific file contents"""

    def _handle_exit(self) -> str:
        """Handle exit command."""
        return "exit"
        
    def _handle_ls(self) -> str:
        """Handle ls command."""
        files = glob.glob("**/*", recursive=True)
        return "Files in current directory:\n" + "\n".join(f"• {f}" for f in files)

    def _get_file_content(self, filename: str) -> str:
        """Get content of a file if it exists."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None

    def _get_context(self, query: str) -> Tuple[str, str]:
        """Get relevant context based on the query."""
        # Default to sonar-pro for most queries
        model = "sonar-pro"
        
        # Add context about the codebase
        context = """You are analyzing a Python codebase. You have access to the files in the current directory. 
Here are some key files and their purposes:
- cli.py: Main CLI entry point
- agents/perplexity.py: Perplexity API integration
- ui/terminal.py: Terminal UI using Rich library

You can read and analyze these files. When asked about code, provide specific analysis and explanations."""

        # Check if query mentions specific files
        python_files = glob.glob("**/*.py", recursive=True)
        mentioned_files = []
        
        for file in python_files:
            if file.lower() in query.lower():
                content = self._get_file_content(file)
                if content:
                    mentioned_files.append(f"\n\nContent of {file}:\n```python\n{content}\n```")
        
        if mentioned_files:
            context += "\n" + "\n".join(mentioned_files)

        return model, context

    async def process_query(self, query: str) -> str:
        """Process query with intelligence layer."""
        # Check for local commands first
        cmd = query.lower().strip()
        if cmd in self.commands:
            return self.commands[cmd]()
            
        try:
            # Get appropriate model and context
            model, context = self._get_context(query)
            
            # Construct the message with context
            messages = [
                {
                    "role": "system",
                    "content": context
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            payload = {
                "model": model,
                "messages": messages
            }
            
            response = await self.client.post(
                "/chat/completions",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            return "No response received from the model."
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid API key. Please check your PPLX_API_KEY environment variable."
            return f"API error: {str(e)}"
        except httpx.TimeoutException:
            return "Request timed out. Please try again."
        except Exception as e:
            return f"Unexpected error: {str(e)}"
        
    async def close(self):
        """Close the HTTP client."""
        try:
            if self.client:
                await self.client.aclose()
        except Exception:
            # Silently handle any cleanup errors
            pass 