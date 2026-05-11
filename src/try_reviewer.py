"""Standalone Claude reviewer demo."""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.reviewer.claude_reviewer import ClaudeReviewer
from src.parsers.ast_analyzer import ASTAnalyzer

console = Console()


BUGGY_CODE = '''
import os

def divide(a, b):
    return a / b

def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

def read_file(path):
    f = open(path, "r")
    content = f.read()
    return content

PASSWORD = "admin123"

def process_items(items):
    result = []
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == items[j] and i != j:
                result.append(items[i])
    return result
'''


def main():
    console.print("\n[bold cyan]═══ Claude Reviewer Demo ═══[/bold cyan]\n")
    
    analyzer = ASTAnalyzer()
    ast_result = analyzer.analyze(BUGGY_CODE, "buggy.py")
    
    console.print(f"[dim]AST: {len(ast_result.functions)} funcs, avg complexity {ast_result.avg_complexity}[/dim]\n")
    
    reviewer = ClaudeReviewer()
    
    cost = reviewer.estimate_cost(BUGGY_CODE)
    console.print(Panel.fit(
        f"Input tokens: ~{cost['estimated_input_tokens']}\n"
        f"Output tokens: ~{cost['estimated_output_tokens']}\n"
        f"Estimated cost: ${cost['estimated_cost_usd']}",
        title="💰 Cost Estimate",
    ))
    
    console.print("\n[yellow]→ Calling Claude API...[/yellow]\n")
    
    review = reviewer.review_file(
        filename="buggy.py",
        code=BUGGY_CODE,
        ast_analysis=ast_result,
        dependencies=0,
    )
    
    console.print(Panel.fit(
        f"[bold]Score:[/bold] {review.overall_score}/10\n"
        f"[bold]Issues:[/bold] {len(review.issues)}\n"
        f"[bold]Summary:[/bold] {review.summary}",
        title=f"📋 Review: {review.filename}",
    ))
    
    if review.issues:
        table = Table(title="🐛 Issues", show_lines=True)
        table.add_column("Line", justify="center", style="dim")
        table.add_column("Severity", justify="center")
        table.add_column("Category", style="cyan")
        table.add_column("Message")
        table.add_column("Fix", style="green")
        
        severity_colors = {
            "critical": "red",
            "high": "orange1",
            "medium": "yellow",
            "low": "blue",
            "info": "dim",
        }
        
        for issue in review.issues:
            color = severity_colors.get(issue.severity, "white")
            table.add_row(
                str(issue.line),
                f"[{color}]{issue.severity}[/{color}]",
                issue.category,
                issue.message,
                issue.suggestion,
            )
        
        console.print(table)
    
    counts = review.issue_count_by_severity()
    console.print(f"\n[dim]Breakdown: {counts}[/dim]")


if __name__ == "__main__":
    main()