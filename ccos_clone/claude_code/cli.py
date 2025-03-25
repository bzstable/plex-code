"""
Command line interface for the application.
"""

import typer
import asyncio
from .agents.perplexity import PerplexityAPI
from .ui.terminal import TerminalUI

app = typer.Typer()

async def run_interactive(api: PerplexityAPI, ui: TerminalUI):
    """Run the interactive CLI loop."""
    try:
        await ui.interactive_prompt(api.process_query)
    finally:
        await api.close()

@app.command()
def main(workspace: str = None):
    """Start the interactive CLI."""
    ui = TerminalUI()
    
    try:
        ui.show_welcome()
        api = PerplexityAPI()
        
        # Run the event loop
        asyncio.run(run_interactive(api, ui))
        
    except ValueError as e:
        # API key related errors
        print(f"\nError: {str(e)}")
        print("\nTo set your API key, run:")
        print("    $env:PPLX_API_KEY='your-api-key-here'    # PowerShell")
        print("    export PPLX_API_KEY='your-api-key-here'  # Bash/Zsh")
        raise typer.Exit(1)
    except Exception as e:
        ui.show_error(f"Application error: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 