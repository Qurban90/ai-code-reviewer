"""Demo runner for priority queue and cache."""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from src.priority.prioritizer import ReviewPrioritizer, FileMetrics
from src.cache.review_cache import ReviewCache

console = Console()


def demo_priority():
    console.print("\n[bold cyan]═══ PRIORITY QUEUE DEMO ═══[/bold cyan]\n")
    
    pq = ReviewPrioritizer()
    
    files = [
        FileMetrics("simple_helper.py", complexity=1, dependencies=0, lines_changed=5),
        FileMetrics("auth.py", complexity=8, dependencies=5, lines_changed=120),
        FileMetrics("config.py", complexity=2, dependencies=1, lines_changed=10),
        FileMetrics("database.py", complexity=12, dependencies=8, lines_changed=200),
        FileMetrics("utils.py", complexity=4, dependencies=3, lines_changed=30),
        FileMetrics("readme_typo.py", complexity=1, dependencies=0, lines_changed=2),
    ]
    
    for m in files:
        pq.add(m)
    
    console.print(f"[green]✓[/green] {pq.size()} fayl prioritizer-ə əlavə edildi\n")
    
    table = Table(title="🎯 Review Sırası (yuxarı = ən vacib)")
    table.add_column("#", style="dim")
    table.add_column("Fayl", style="cyan")
    table.add_column("Score", justify="right", style="yellow")
    table.add_column("Cmplx", justify="right")
    table.add_column("Deps", justify="right")
    table.add_column("Lines", justify="right")
    
    top = pq.top_n(10)
    for i, f in enumerate(top, 1):
        table.add_row(
            str(i),
            f.filename,
            f"{-f.priority:.1f}",
            str(f.complexity),
            str(f.dependencies),
            str(f.lines_changed),
        )
    console.print(table)


def demo_cache():
    console.print("\n[bold cyan]═══ CACHE DEMO ═══[/bold cyan]\n")
    
    cache = ReviewCache(cache_dir="review_cache")
    cache.clear()
    
    code1 = "def add(a, b):\n    return a + b"
    code2 = "def sub(a, b):\n    return a - b"
    
    review1 = {"issues": [], "summary": "Looks fine."}
    review2 = {"issues": [{"line": 1, "msg": "Test"}], "summary": "Has issue."}
    
    cache.set(code1, review1)
    cache.set(code2, review2)
    console.print(f"[green]✓[/green] 2 review cache-ə yazıldı")
    
    hit = cache.get(code1)
    console.print(f"[green]✓[/green] code1 üçün cache hit: {hit.review_data}")
    
    new_code = "def mul(a, b):\n    return a * b"
    miss = cache.get(new_code)
    console.print(f"[yellow]○[/yellow] code3 (yeni) üçün cache miss: {miss}")
    
    same_code = "def add(a, b):\n    return a + b"
    same_hit = cache.get(same_code)
    console.print(f"[green]✓[/green] eyni code yenidən: cache hit ({same_hit is not None})")
    
    console.print(Panel.fit(
        f"[bold]Entries:[/bold] {cache.stats()['entries']}\n"
        f"[bold]Disk files:[/bold] {cache.stats()['disk_files']}\n"
        f"[bold]Cache dir:[/bold] {cache.stats()['cache_dir']}",
        title="📊 Cache Stats",
    ))


if __name__ == "__main__":
    demo_priority()
    demo_cache()