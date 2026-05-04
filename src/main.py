"""
AI Code Reviewer — Main FastAPI Application
"""
from fastapi import FastAPI
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

console = Console()

app = FastAPI(
    title="AI Code Reviewer",
    description="Automated PR review using Claude AI",
    version="0.1.0",
)


@app.get("/")
async def root():
    """Health check endpoint."""
    console.print("[green]✓[/green] Root endpoint hit")
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
            "config_loaded": True,
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)