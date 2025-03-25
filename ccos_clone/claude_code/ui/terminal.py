"""
Terminal UI design using rich library.
Handles all terminal rendering and user interaction.
"""

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.layout import Layout
from rich.style import Style
from rich.text import Text
from rich.syntax import Syntax
from rich.align import Align
from typing import Optional, Callable
import asyncio

# Perplexity theme color
THEME_COLOR = "#00c5e0"

class TerminalUI:
    def __init__(self):
        self.console = Console()
        
    def show_welcome(self):
        """Display welcome message."""
        # Welcome message in a box
        welcome_text = Text()
        welcome_text.append("Plex Code", style=f"bold {THEME_COLOR}")
        welcome_text.append(" - Powered by Perplexity AI", style="white")
        
        welcome_panel = Panel(
            Align.center(welcome_text),
            border_style=THEME_COLOR,
            padding=(1, 2)
        )
        
        # How to use guide (outside the box)
        usage_text = Text()
        usage_text.append("\nHow to use:\n\n", style="bold white")
        usage_text.append("• Just type your question or command naturally\n", style="dim white")
        usage_text.append("• Ask about code, get explanations, or request analysis\n", style="dim white")
        usage_text.append("• Type ", style="dim white")
        usage_text.append("help", style=THEME_COLOR)
        usage_text.append(" to see available commands\n", style="dim white")
        usage_text.append("• Type ", style="dim white")
        usage_text.append("exit", style=THEME_COLOR)
        usage_text.append(" to quit\n", style="dim white")
        
        # Print everything with proper spacing
        self.console.print("\n")  # Add padding at top
        self.console.print(Align.center(welcome_panel))
        self.console.print(Align.center(usage_text))
        self.console.print("\n")  # Add padding at bottom
        
    async def get_input(self, prompt: str = "> ") -> str:
        """Get user input with styled prompt."""
        self.console.print(prompt, style=THEME_COLOR, end="")
        return await asyncio.get_event_loop().run_in_executor(None, input)
        
    def show_thinking(self, message: str = "Processing"):
        """Show processing message."""
        self.console.print(f"\n{message}...\n", style=THEME_COLOR)
        
    def show_error(self, message: str):
        """Display error message."""
        self.console.print(f"\n[red]Error:[/red] {message}\n")
        
    def show_success(self, message: str):
        """Display success message."""
        self.console.print(f"\n[{THEME_COLOR}]{message}[/{THEME_COLOR}]\n")
        
    def show_code(self, code: str, language: str = "text"):
        """Display response text."""
        if code and code.strip():
            # Create a panel with the response
            panel = Panel(
                code,
                title="Response",
                border_style=THEME_COLOR,
                padding=(1, 2)
            )
            self.console.print(panel)
            self.console.print()  # Add a blank line after response
        
    async def interactive_prompt(self, handler: Callable):
        """Start interactive prompt loop."""
        while True:
            try:
                command = await self.get_input()
                if command.lower() in ["exit", "quit"]:
                    self.show_success("Goodbye!")
                    break
                    
                self.show_thinking()
                response = await handler(command)
                if response:
                    self.show_code(response)
                    
            except KeyboardInterrupt:
                self.show_success("\nGoodbye!")
                break
            except Exception as e:
                self.show_error(str(e)) 