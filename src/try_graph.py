"""Quick test runner for dependency graph."""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.graph.dependency_graph import DependencyGraphBuilder

console = Console()


def main():
    builder = DependencyGraphBuilder()
    
    # Sample layihəni analiz et
    sample_dir = "src/graph/sample_project"
    console.print(f"\n[bold cyan]🔍 Analiz edilir:[/bold cyan] {sample_dir}\n")
    
    graph = builder.build_from_directory(sample_dir)
    analysis = builder.analyze()
    
    # Ümumi statistika
    console.print(Panel.fit(
        f"[bold]Fayllar:[/bold] {analysis.total_files}\n"
        f"[bold]Import-lar:[/bold] {analysis.total_imports}\n"
        f"[bold]Cycle var?[/bold] {'[red]BƏLİ ⚠[/red]' if analysis.has_cycles else '[green]Xeyr ✓[/green]'}",
        title="📊 Ümumi Statistika",
    ))
    
    # Cycle-lar
    if analysis.cycles:
        console.print("\n[bold red]⚠ Tapılan dairəvi import-lar:[/bold red]")
        for i, cycle in enumerate(analysis.cycles, 1):
            cycle_str = " → ".join(cycle) + f" → {cycle[0]}"
            console.print(f"  {i}. {cycle_str}")
    
    # Ən çox import edilən fayllar
    if analysis.most_imported:
        table = Table(title="🎯 Ən çox import edilən (kritik fayllar)")
        table.add_column("Modul", style="cyan")
        table.add_column("Neçə yerdə import olunur", justify="right", style="yellow")
        for module, count in analysis.most_imported:
            table.add_row(module, str(count))
        console.print(table)
    
    # Ən çox asılılığı olan fayllar
    if analysis.most_dependencies:
        table = Table(title="🔗 Ən çox asılılığı olan fayllar")
        table.add_column("Modul", style="magenta")
        table.add_column("Neçə fayl import edir", justify="right", style="yellow")
        for module, count in analysis.most_dependencies:
            table.add_row(module, str(count))
        console.print(table)
    
    # Impact analysis demo
    console.print("\n[bold]🎯 Impact Analysis Demo:[/bold]")
    test_module = "models"
    impact = builder.get_impact(test_module)
    if impact:
        console.print(f"  Əgər [yellow]{test_module}[/yellow] dəyişərsə, bu fayllar təsirlənəcək:")
        for m in impact:
            console.print(f"    → {m}")
    
    # Render PNG
    console.print("\n[bold]🖼  Qraf şəkil kimi yadda saxlanılır...[/bold]")
    try:
        path = builder.render_as_image("graphs/sample_dependency_graph")
        console.print(f"  [green]✓[/green] Yaradıldı: [cyan]{path}[/cyan]")
        console.print(f"  [dim]File Explorer-də açıb baxa bilərsən![/dim]")
    except Exception as e:
        console.print(f"  [red]✗ Xəta:[/red] {e}")
        console.print(f"  [dim]Graphviz quraşdırılıb? `dot -V` yoxla.[/dim]")


if __name__ == "__main__":
    main()