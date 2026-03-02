import typer
import random
import json
import copy
from pathlib import Path
from rich.console import Console
from . import __version__
from .runner import Runner
from .reporter import Reporter
from .redactor import RegexRedactor
from .mutator import PromptMutator
from .judge import JudgeFeedbackLoop
from .adapters.openai import OpenAIAdapter
from .adapters.ollama import OllamaAdapter
from .adapters.anthropic import AnthropicAdapter
from .adapters.huggingface import HuggingFaceAdapter
from .adapters.gemini import GeminiAdapter
from .adapters.mistral import MistralAdapter
from .adapters.exploitrank import ExploitRankBridge

app = typer.Typer(help="DarkPrompt: Security-focused prompt analysis and LLM interaction tool.")
console = Console()

@app.command()
def run(
    target: str = typer.Option("openai", "--target", "-t", help="Target adapter"),
    pack_dir: Path = typer.Option(None, "--pack", "-p", help="Directory containing the test pack"),
    out_dir: Path = typer.Option(Path("./out"), "--out", "-o", help="Output directory"),
    model: str = typer.Option(None, "--model", "-m", help="Model name"),
    redact: str = typer.Option(None, "--redact", help="Regex patterns for redaction"),
    base_url: str = typer.Option(None, "--base-url", help="Override base URL"),
    mutate: bool = typer.Option(False, "--mutate", help="Apply random prompt mutations"),
    format: str = typer.Option("markdown", "--format", "-f", help="Report format"),
    sensitivity: bool = typer.Option(False, "--sensitivity", "-s", help="Run systematic mutation sensitivity analysis"),
    adaptive: bool = typer.Option(False, "--adaptive", "-a", help="Enable LLM-as-a-judge feedback loop for adaptive retries"),
    exploit_rank: bool = typer.Option(False, "--exploit-rank", "--er", help="Pull latest real exploits from ExploitRank EIE")
):
    """
    Run a security test pack against a target adapter.
    """
    console.print(f"[bold blue]Starting DarkPrompt Run (v{__version__})[/bold blue]")
    
    if not model:
        defaults = {"openai": "gpt-3.5-turbo", "anthropic": "claude-3-5-sonnet-20241022", "ollama": "mistral", "huggingface": "meta-llama/Llama-3.2-3B-Instruct", "gemini": "gemini-1.5-flash", "mistral": "mistral-large-latest"}
        model = defaults.get(target, "default")

    console.print(f"Target: [green]{target}[/green] | Model: [green]{model}[/green]")
    
    # Initialize components
    adapters = {
        "openai": OpenAIAdapter, "ollama": OllamaAdapter, "anthropic": AnthropicAdapter, 
        "huggingface": HuggingFaceAdapter, "gemini": GeminiAdapter, "mistral": MistralAdapter
    }
    
    if target not in adapters:
        console.print(f"[red]Unknown target: {target}[/red]")
        raise typer.Exit(1)
        
    adapter_cls = adapters[target]
    adapter_kwargs = {"model": model}
    if target == "ollama" and base_url: adapter_kwargs["base_url"] = base_url
    adapter = adapter_cls(**adapter_kwargs)

    redactor = RegexRedactor(patterns=redact.split(",")) if redact else None
    mutator = PromptMutator(out_dir=str(out_dir / "media"))
    runner = Runner(adapter=adapter, redactor=redactor)
    judge = JudgeFeedbackLoop(target_adapter=adapter) if adaptive else None
    
    try:
        all_traces = []
        
        # 1. Load pack cases if pack_dir is provided
        pack = None
        if pack_dir:
            pack = runner.load_pack(pack_dir)
            console.print(f"Loaded pack: [bold]{pack.name}[/bold]")
        else:
            # Create empty pack if only running ExploitRank
            from .models import TestPack
            pack = TestPack(name="ExploitRank Bridge Run", description="Run pulling real-world exploits", version=__version__)

        # 2. Pull from ExploitRank if requested
        if exploit_rank:
            console.print("[yellow]ExploitRank Bridge active. Pulling latest real-world exploits...[/yellow]")
            bridge = ExploitRankBridge()
            exploits = bridge.get_latest_exploits(limit=3)
            if not exploits:
                console.print("[red]No real exploits found in EIE database. Ensure ExploitRank is populated.[/red]")
            else:
                for exp in exploits:
                    case = bridge.generate_case_from_exploit(exp)
                    pack.cases.append(case)
                    console.print(f"  Added real-world case: [bold]{case.id}[/bold]")

        if not pack.cases:
            console.print("[red]No test cases loaded (neither from pack nor ExploitRank).[/red]")
            raise typer.Exit(1)

        # 3. Process Cases (Standard, Adaptive, or Sensitivity)
        if sensitivity:
            console.print("[yellow]Sensitivity Analysis enabled. Running systematic mutations...[/yellow]")
            mutation_names = ["Leet", "Base64", "Noise", "Reverse", "Caesar", "Homoglyph", "Split", "OCR"]
            for case in pack.cases:
                # Original
                console.print(f"  Testing Case {case.id} [Original]...")
                all_traces.append(runner.run_case(case))
                
                # Mutated variants
                variants = mutator.apply_all(case.prompt)
                # variants[0] is original
                for i, v_prompt in enumerate(variants[1:]):
                    m_name = mutation_names[i] if i < len(mutation_names) else f"Mutation-{i}"
                    console.print(f"  Testing Case {case.id} [{m_name}]...")
                    m_case = copy.deepcopy(case)
                    m_case.prompt = v_prompt
                    m_case.id = f"{case.id}-{m_name}"
                    all_traces.append(runner.run_case(m_case))
        elif adaptive:
            console.print("[yellow]Adaptive Mode enabled. Retrying on refusal with Judge feedback...[/yellow]")
            for case in pack.cases:
                console.print(f"  Running adaptive case: [bold]{case.id}[/bold]")
                all_traces.append(judge.run_adaptive_case(case))
        else:
            if mutate:
                for case in pack.cases:
                    case.prompt = random.choice(mutator.apply_all(case.prompt)[1:])
            # standard run
            for case in pack.cases:
                all_traces.append(runner.run_case(case))
        
        # Inject metadata
        for trace in all_traces:
            base_id = trace.test_case_id.split("-")[0]
            original_case = next((c for c in pack.cases if c.id == base_id or trace.test_case_id.startswith(c.id)), None)
            if original_case:
                trace.metadata['category'] = original_case.category

        out_dir.mkdir(parents=True, exist_ok=True)
        reporter = Reporter()
        report_path = (reporter.generate_json(pack, all_traces, out_dir) if format == "json" 
                       else reporter.generate_markdown(pack, all_traces, out_dir))
        
        console.print(f"[bold green]Audit complete![/bold green] Report: [blue]{report_path}[/blue]")
    except Exception as e:
        console.print(f"[red]Error during run: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def version():
    console.print(f"DarkPrompt v{__version__}")

if __name__ == "__main__":
    app()
