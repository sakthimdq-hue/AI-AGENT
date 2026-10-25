"""
AegisDev Interactive CLI
Run autonomous software engineering tasks directly from your terminal!
"""
import sys
import asyncio
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table

from core.llm_client import LLMClient
from core.agent import AutonomousAgent

console = Console()

def load_config():
    config_path = "config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "api_key": os.environ.get("GEMINI_API_KEY", ""),
        "base_url": ""
    }

async def run_cli_agent(instruction: str):
    config = load_config()
    api_key = config.get("api_key") or os.environ.get("GEMINI_API_KEY") or ""
    provider = config.get("provider", "gemini")
    model = config.get("model", "gemini-2.5-flash")

    console.print(Panel.fit(
        f"[bold cyan]🤖 AegisDev - Autonomous AI Software Engineer[/bold cyan]\n"
        f"[dim]Provider:[/dim] [yellow]{provider.upper()}[/yellow] | [dim]Model:[/dim] [yellow]{model}[/yellow]\n"
        f"[dim]Task:[/dim] [white]{instruction}[/white]",
        border_style="cyan"
    ))

    if provider == "gemini" and not api_key:
        console.print("[bold red]❌ Error: GEMINI_API_KEY is not set![/bold red]")
        console.print("Please set your free Gemini API key in [bold yellow]config.json[/bold yellow] or via environment variable:")
        console.print("[dim]export GEMINI_API_KEY='AIzaSy...'[/dim]")
        console.print("Get a free key here: [link=https://aistudio.google.com/]https://aistudio.google.com/[/link]\n")
        return

    client = LLMClient(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=config.get("base_url")
    )
    agent = AutonomousAgent(llm_client=client)

    with console.status("[bold green]Agent working on task...[/bold green]", spinner="dots"):
        async for event in agent.run(instruction):
            etype = event.get("type")

            if etype == "step_begin":
                step = event.get("step")
                console.print(f"\n[bold magenta]━━━ Step {step} ━━━[/bold magenta]")

            elif etype == "thought":
                console.print(Panel(event.get("content", ""), title="[bold yellow]🧠 Agent Thought[/bold yellow]", border_style="yellow"))

            elif etype == "tool_start":
                tool = event.get("tool")
                args = json.dumps(event.get("arguments", {}), indent=2)
                console.print(f"[bold blue]🔧 Tool Call:[/bold blue] [cyan]{tool}[/cyan]")
                console.print(Syntax(args, "json", theme="monokai", line_numbers=False))

            elif etype == "tool_result":
                res = json.dumps(event.get("result", {}), indent=2)
                if len(res) > 500:
                    res = res[:500] + "... (truncated)"
                console.print(f"[bold green]✔ Result:[/bold green] [dim]{res}[/dim]")

            elif etype == "completed":
                console.print("\n")
                console.print(Panel(
                    Markdown(event.get("summary", "")),
                    title="[bold green]🎉 Task Completed Successfully![/bold green]",
                    border_style="green"
                ))

            elif etype == "error":
                console.print(f"[bold red]❌ Error in step {event.get('step')}:[/bold red] {event.get('message')}")

            elif etype == "max_steps_reached":
                console.print(f"[bold orange3]⚠ {event.get('message')}[/bold orange3]")

def main():
    if len(sys.argv) > 1:
        instruction = " ".join(sys.argv[1:])
    else:
        console.print("[bold cyan]Enter your instruction for the AI Software Engineer:[/bold cyan]")
        try:
            instruction = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            return

    if not instruction:
        console.print("[yellow]No instruction provided. Exiting.[/yellow]")
        return

    asyncio.run(run_cli_agent(instruction))

if __name__ == "__main__":
    main()
