"""
AI Code Reviewer — Main FastAPI Application
"""
import os
import hmac
import hashlib
import json
from fastapi import FastAPI, Request, HTTPException, Header
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

console = Console()

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "").encode()

app = FastAPI(
    title="AI Code Reviewer",
    description="Automated PR review using Claude AI",
    version="0.1.0",
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "AI Code Reviewer",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "checks": {
            "server": "ok",
            "config_loaded": bool(WEBHOOK_SECRET),
        },
    }


def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature for security."""
    if not signature_header:
        return False
    
    if not WEBHOOK_SECRET:
        console.print("[yellow]⚠[/yellow] No webhook secret configured")
        return True  # Skip verification in dev if no secret
    
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET,
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature_header)


@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None),
):
    """Receive GitHub webhook events."""
    body = await request.body()
    
    # Verify signature
    if not verify_signature(body, x_hub_signature_256):
        console.print("[red]✗[/red] Invalid signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = json.loads(body)
    event_type = x_github_event
    
    console.print(f"\n[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]")
    console.print(f"[green]✓[/green] Webhook received: [bold]{event_type}[/bold]")
    
    # Handle pull request events
    if event_type == "pull_request":
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")
        pr_title = pr.get("title")
        repo = payload.get("repository", {}).get("full_name")
        
        console.print(f"  Action: [yellow]{action}[/yellow]")
        console.print(f"  Repo: {repo}")
        console.print(f"  PR #{pr_number}: {pr_title}")
        
        # We only care about new PRs and updates
        if action in ["opened", "synchronize", "reopened"]:
            console.print(f"  [green]→ Will review this PR[/green]")
            # TODO: Day 3+ — actual review logic
        else:
            console.print(f"  [dim]→ Ignoring action[/dim]")
    
    elif event_type == "ping":
        console.print(f"  [green]→ Ping successful! Webhook is working.[/green]")
    
    else:
        console.print(f"  [dim]→ Event type not handled[/dim]")
    
    console.print(f"[cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/cyan]\n")
    
    return {"status": "received", "event": event_type}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)