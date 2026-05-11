"""Standalone orchestrator demo (GitHub-suz)."""
from src.orchestrator import ReviewOrchestrator
from src.main import display_review_context


SAMPLE_FILES = {
    "main.py": """
from utils import format_data
from db import get_user

def run():
    user = get_user(1)
    print(format_data(user))
""",
    "utils.py": """
from helpers import safe_str

def format_data(x):
    if x is None:
        return "none"
    elif isinstance(x, dict):
        if "name" in x:
            return safe_str(x["name"])
        return "no_name"
    return safe_str(x)
""",
    "helpers.py": """
def safe_str(x):
    return str(x) if x else "N/A"
""",
    "db.py": """
from models import User

def get_user(uid):
    if uid <= 0:
        return None
    return User(id=uid, name=f"User-{uid}")
""",
    "models.py": """
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
""",
}

CHANGED_LINES = {
    "main.py": 5,
    "utils.py": 80,
    "helpers.py": 3,
    "db.py": 45,
    "models.py": 10,
}


if __name__ == "__main__":
    orch = ReviewOrchestrator(max_files=3)
    ctx = orch.process_pr(
        pr_number=99,
        repo="demo/test-repo",
        files=SAMPLE_FILES,
        changed_lines=CHANGED_LINES,
    )
    display_review_context(ctx)