import asyncio
import importlib.util
import sys
import os
import typer
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

from .agent import BaseAgent
from .types import TokenEvent, ThoughtEvent, ToolCallEvent, ToolResultEvent, ErrorEvent

app = typer.Typer()
console = Console()

def load_agent_from_file(path: str) -> BaseAgent:
    """Load an agent instance from a python file."""
    if ":" in path:
        file_path, class_name = path.split(":")
    else:
        file_path = path
        class_name = "Agent" # Default convention

    if not os.path.exists(file_path):
        console.print(f"[red]Error: File {file_path} not found.[/red]")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("user_agent_module", file_path)
    if spec is None or spec.loader is None:
        console.print(f"[red]Error: Could not load module from {file_path}[/red]")
        sys.exit(1)
        
    module = importlib.util.module_from_spec(spec)
    sys.modules["user_agent_module"] = module
    spec.loader.exec_module(module)

    if not hasattr(module, class_name):
        console.print(f"[red]Error: Class '{class_name}' not found in {file_path}[/red]")
        # Try to find any subclass of BaseAgent
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseAgent) and attr is not BaseAgent:
                console.print(f"[yellow]Found agent class: {attr_name}, using it.[/yellow]")
                return attr()
        sys.exit(1)
    
    agent_class = getattr(module, class_name)
    return agent_class()

async def run_loop(agent: BaseAgent):
    """Main interactive loop."""
    session = PromptSession(style=Style.from_dict({
        'prompt': '#ansigreen bold',
    }))
    
    console.print(Panel(f"[bold blue]Welcome to AgentIO CLI[/bold blue]\nLoaded Agent: {agent.config.name}"))

    while True:
        try:
            user_input = await session.prompt_async("User> ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            if not user_input.strip():
                continue

            # UI State for streaming
            current_response = Text()
            
            with Live(Panel(current_response, title="Assistant", border_style="blue"), console=console, refresh_per_second=10) as live:
                async for event in agent.run(user_input):
                    if isinstance(event, TokenEvent):
                        current_response.append(event.content)
                        live.update(Panel(current_response, title="Assistant", border_style="blue"))
                    
                    elif isinstance(event, ThoughtEvent):
                        live.update(Panel(f"[dim]{event.content}[/dim]\n\n{current_response}", title="Thinking...", border_style="yellow"))
                        await asyncio.sleep(0.1) # brief pause to see thought
                        
                    elif isinstance(event, ToolCallEvent):
                        live.update(Panel(f"[bold cyan]Tool Call: {event.tool_name}({event.tool_args})[/bold cyan]\n\n{current_response}", title="Tool Use", border_style="cyan"))
                        
                    elif isinstance(event, ToolResultEvent):
                        live.update(Panel(f"[bold green]Tool Result: {event.result}[/bold green]\n\n{current_response}", title="Tool Result", border_style="green"))
                        
                    elif isinstance(event, ErrorEvent):
                        console.print(f"[red]Error: {event.message}[/red]")

            console.print() # Newline after response

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

@app.command()
def run(
    agent_path: str = typer.Argument(..., help="Path to the agent file (e.g., my_agent.py or my_agent.py:MyClass)"),
):
    """
    Run an agent in interactive TUI mode.
    """
    agent = load_agent_from_file(agent_path)
    asyncio.run(run_loop(agent))

@app.command()
def init(name: str):
    """
    Initialize a new agent project.
    """
    os.makedirs(name, exist_ok=True)
    
    # Create agent.py
    with open(f"{name}/agent.py", "w") as f:
        f.write('''from agentio.agent import BaseAgent, AgentEvent, TokenEvent, ThoughtEvent
from typing import AsyncIterator
import asyncio

class MyAgent(BaseAgent):
    """
    My Custom Agent
    """
    async def run(self, input_text: str) -> AsyncIterator[AgentEvent]:
        self.add_message("user", input_text)
        
        yield ThoughtEvent(content="Processing user input...")
        yield TokenEvent(content="Hello! I received: " + input_text)
        
        self.add_message("assistant", "Hello! I received: " + input_text)
''')
    
    # Create valid pyproject.toml
    with open(f"{name}/.env", "w") as f:
        f.write("# keys here\n")

    console.print(f"[green]Created new agent project in ./{name}[/green]")
    console.print(f"Run it with: [bold]agentio run {name}/agent.py[/bold]")

if __name__ == "__main__":
    app()
