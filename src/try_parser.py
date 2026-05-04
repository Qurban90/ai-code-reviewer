"""Quick test runner for AST analyzer."""
from rich.console import Console
from rich.table import Table
from src.parsers.ast_analyzer import ASTAnalyzer

console = Console()


def main():
    # Test faylını oxu
    with open("src/parsers/test_sample.py", "r", encoding="utf-8") as f:
        code = f.read()
    
    # Analiz et
    analyzer = ASTAnalyzer()
    result = analyzer.analyze(code, "test_sample.py")
    
    # Nəticəni göstər
    console.print(f"\n[bold cyan]📄 Fayl:[/bold cyan] {result.filename}")
    console.print(f"[cyan]Sətir sayı:[/cyan] {result.total_lines}")
    console.print(f"[cyan]Orta mürəkkəblik:[/cyan] {result.avg_complexity}")
    
    if result.has_syntax_error:
        console.print(f"[red]✗ Syntax error: {result.error_message}[/red]")
        return
    
    # Funksiyalar cədvəli
    if result.functions:
        table = Table(title="🔧 Funksiyalar", show_header=True)
        table.add_column("Ad", style="green")
        table.add_column("Sətir", justify="center")
        table.add_column("Argümentlər", style="yellow")
        table.add_column("Mürəkkəblik", justify="center")
        table.add_column("Async?", justify="center")
        
        for fn in result.functions:
            complexity_color = "green" if fn.complexity <= 5 else "yellow" if fn.complexity <= 10 else "red"
            table.add_row(
                fn.name,
                f"{fn.line_start}-{fn.line_end}",
                ", ".join(fn.args) or "—",
                f"[{complexity_color}]{fn.complexity}[/{complexity_color}]",
                "✓" if fn.is_async else "—",
            )
        console.print(table)
    
    # Class-lar
    if result.classes:
        table = Table(title="🏛  Class-lar", show_header=True)
        table.add_column("Ad", style="magenta")
        table.add_column("Sətir", justify="center")
        table.add_column("Metodlar", style="yellow")
        table.add_column("Base", style="cyan")
        
        for cls in result.classes:
            table.add_row(
                cls.name,
                f"{cls.line_start}-{cls.line_end}",
                ", ".join(cls.methods) or "—",
                ", ".join(cls.base_classes) or "—",
            )
        console.print(table)
    
    # Import-lar
    if result.imports:
        console.print(f"\n[bold]📦 Import-lar ({len(result.imports)}):[/bold]")
        for imp in result.imports:
            arrow = "from →" if imp.is_from_import else "import"
            console.print(f"  [dim]Line {imp.line}:[/dim] {arrow} {imp.module} → {', '.join(imp.names)}")


if __name__ == "__main__":
    main()