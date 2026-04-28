import os
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from evaluator import evaluate_many

console = Console()

# ---------------------------------------------------------------
# Sample docs to evaluate — we'll use real changelog entries
# from our changelog generator as test cases
# ---------------------------------------------------------------

SAMPLE_DOCS = [
    {
        "label": "Good entry — RLS Tester",
        "content": """
## RLS Tester (Feature Preview)

A new RLS Tester is available as an opt-in feature preview in Supabase Studio. 
You can now run SQL queries impersonating specific user roles (anonymous or 
authenticated), observe which RLS policies are evaluated during execution, and 
identify misconfigured policies. Enable it via the Feature Preview panel in 
Studio settings.

This addresses a long-standing gap in verifying the correctness of RLS policy 
configurations without having to test in production.
"""
    },
    {
        "label": "Weak entry — vague improvement",
        "content": """
## Improvements

Various bug fixes and performance improvements have been made to the dashboard. 
Users may notice things working better. Some issues that were reported have been 
addressed in this release.
"""
    },
    {
        "label": "Medium entry — accurate but incomplete",
        "content": """
## OAuth Provider Toggle

Custom OAuth providers now support an enable/disable toggle. 
Disabling shows a confirmation dialog.
"""
    },
    {
        "label": "Good entry — technical depth",
        "content": """
## logs:all Feature Flag for Self-Hosted Studio

A new `logs:all` feature flag (default: `true`) allows self-hosted Studio 
deployments to hide all Logs pages when Logflare is not configured.

When set to `false`:
- The Logs sidebar entry is hidden
- All Command-K log shortcuts are suppressed  
- Navigating directly to any logs route renders a soft 404

Set `ENABLED_FEATURES_LOGS_ALL=false` in your environment to disable logs 
without requiring a custom Studio build. Hosted Supabase deployments are 
unaffected by this flag.
"""
    }
]


def save_results(results: list[dict]):
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"results/eval_{timestamp}.json"
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)
    return filepath


def display_results(results: list[dict]):
    console.print()
    console.print(Panel.fit(
        "[bold white]Documentation Quality Evaluation[/bold white]",
        border_style="dim"
    ))
    console.print()

    # Summary table
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold dim")
    table.add_column("Entry", style="white", min_width=30)
    table.add_column("Clarity", justify="center", min_width=8)
    table.add_column("Accuracy", justify="center", min_width=8)
    table.add_column("Completeness", justify="center", min_width=12)
    table.add_column("Overall", justify="center", min_width=8)

    def score_color(score):
        if score >= 4.5:
            return f"[bold green]{score}[/bold green]"
        elif score >= 3.5:
            return f"[bold yellow]{score}[/bold yellow]"
        else:
            return f"[bold red]{score}[/bold red]"

    for r in results:
        table.add_row(
            r["label"],
            score_color(r["clarity"]["score"]),
            score_color(r["accuracy"]["score"]),
            score_color(r["completeness"]["score"]),
            score_color(r["overall"]),
        )

    console.print(table)
    console.print()

    # Detailed breakdown
    for r in results:
        console.print(f"[bold white]{r['label']}[/bold white]")
        console.print(f"  [dim]Clarity:[/dim]      {r['clarity']['reasoning']}")
        console.print(f"  [dim]Accuracy:[/dim]     {r['accuracy']['reasoning']}")
        console.print(f"  [dim]Completeness:[/dim] {r['completeness']['reasoning']}")
        console.print(f"  [dim]Summary:[/dim]      {r['summary']}")
        console.print()


def main():
    console.print(f"\n[dim]Evaluating {len(SAMPLE_DOCS)} documentation entries...[/dim]\n")
    results = evaluate_many(SAMPLE_DOCS)

    display_results(results)

    filepath = save_results(results)
    console.print(f"[dim]Results saved to {filepath}[/dim]\n")


if __name__ == "__main__":
    main()