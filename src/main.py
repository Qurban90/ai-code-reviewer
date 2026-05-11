"""
AI Code Reviewer — Main FastAPI Application
"""
import os
import hmac
import hashlib
import json
import logging
from fastapi import FastAPI, Request, HTTPException, Header
from rich.console import Console
from rich.logging import RichHandler
from dotenv import load_dotenv

from src.orchestrator import ReviewOrchestrator

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, show_time=True, show_path=False)],
)
logger = logging.getLogger(__name__)

console = Console()
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

app = FastAPI(title="AI Code Reviewer", version="0.6.0")

orchestrator = ReviewOrchestrator(max_files=5)


@app.get("/")
async def root():
    return {"status": "online", "service": "AI Code Reviewer", "version": "0.6.0"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "config": {
            "webhook_secret": bool(WEBHOOK_SECRET),
            "github_token": bool(GITHUB_TOKEN),
        },
    }


def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False
    if not WEBHOOK_SECRET:
        return True
    expected = "sha256=" + hmac.new(WEBHOOK_SECRET, payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def fetch_pr_files(repo: str, pr_number: int) -> dict:
    """PR faylarını GitHub-dan çək."""
    from github import Github
    if not GITHUB_TOKEN:
        logger.warning("No GITHUB_TOKEN, skipping fetch")
        return {}
    
    try:
        gh = Github(GITHUB_TOKEN)
        repository = gh.get_repo(repo)
        pr = repository.get_pull(pr_number)
        
        files = {}
        changed_lines = {}
        
        for f in pr.get_files():
            if f.filename.endswith(".py") and f.status != "removed":
                try:
                    content = repository.get_contents(f.filename, ref=pr.head.sha)
                    files[f.filename] = content.decoded_content.decode("utf-8")
                    changed_lines[f.filename] = (f.additions or 0) + (f.deletions or 0)
                except Exception as e:
                    logger.warning(f"Could not fetch {f.filename}: {e}")
        
        return {"files": files, "changed_lines": changed_lines}
    except Exception as e:
        logger.error(f"GitHub fetch error: {e}")
        return {}


def display_review_context(ctx) -> None:
    """Pipeline nəticələrini gözəl şəkildə göstər."""
    console.print(f"\n[bold cyan]━━━ PR #{ctx.pr_number} Review Pipeline ━━━[/bold cyan]")
    console.print(f"[dim]Repo:[/dim] {ctx.repo}")
    console.print(f"[dim]Files in PR:[/dim] {len(ctx.files)}")
    
    if ctx.errors:
        console.print(f"\n[red]Errors ({len(ctx.errors)}):[/red]")
        for e in ctx.errors:
            console.print(f"  ✗ {e}")
    
    if ctx.ast_results:
        console.print(f"\n[green]AST analyzed:[/green] {len(ctx.ast_results)} files")
        for fname, ar in ctx.ast_results.items():
            console.print(
                f"  • {fname}: {len(ar.functions)} fns, "
                f"{len(ar.classes)} cls, avg complexity {ar.avg_complexity}"
            )
    
    if ctx.graph_analysis:
        ga = ctx.graph_analysis
        console.print(f"\n[green]Graph:[/green] {ga.total_files} nodes, {ga.total_imports} edges")
        if ga.has_cycles:
            console.print(f"  [red]⚠ {len(ga.cycles)} cycles detected[/red]")
    
    if ctx.review_order:
        console.print(f"\n[green]Review priority:[/green]")
        for i, pf in enumerate(ctx.review_order, 1):
            console.print(
                f"  {i}. {pf.filename} "
                f"[dim](score={-pf.priority:.1f}, cmplx={pf.complexity}, deps={pf.dependencies})[/dim]"
            )
    
    if ctx.cached_files:
        console.print(f"\n[yellow]Cached (skip):[/yellow] {len(ctx.cached_files)}")
        for f in ctx.cached_files:
            console.print(f"  ○ {f}")
    
    if ctx.files_to_review:
        console.print(f"\n[cyan]To review with AI:[/cyan] {len(ctx.files_to_review)}")
        for f in ctx.files_to_review:
            console.print(f"  → {f}")
    
    console.print(f"[bold cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]\n")


@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None),
):
    body = await request.body()
    
    if not verify_signature(body, x_hub_signature_256):
        logger.error("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = json.loads(body)
    
    if x_github_event == "ping":
        logger.info("Ping received — webhook OK")
        return {"status": "pong"}
    
    if x_github_event != "pull_request":
        return {"status": "ignored", "event": x_github_event}
    
    action = payload.get("action")
    if action not in ("opened", "synchronize", "reopened"):
        return {"status": "ignored", "action": action}
    
    pr = payload.get("pull_request", {})
    pr_number = pr.get("number")
    repo = payload.get("repository", {}).get("full_name")
    
    logger.info(f"PR #{pr_number} ({action}) in {repo}")
    
    pr_data = fetch_pr_files(repo, pr_number)
    if not pr_data.get("files"):
        logger.warning("No Python files in PR")
        return {"status": "no_python_files"}
    
    ctx = orchestrator.process_pr(
        pr_number=pr_number,
        repo=repo,
        files=pr_data["files"],
        changed_lines=pr_data["changed_lines"],
    )
    
    display_review_context(ctx)
    
    return {
        "status": "processed",
        "pr": pr_number,
        "files_analyzed": len(ctx.ast_results),
        "files_to_review": len(ctx.files_to_review),
        "cached": len(ctx.cached_files),
        "errors": len(ctx.errors),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)