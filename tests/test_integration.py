"""Integration tests — bütün pipeline-ı yoxlayır."""
import pytest
from src.orchestrator import ReviewOrchestrator


@pytest.fixture
def orch(tmp_path):
    return ReviewOrchestrator(cache_dir=str(tmp_path / "cache"), max_files=5)


def test_full_pipeline_realistic(orch):
    """Real ssenariy: çoxlu fayllar, müxtəlif mürəkkəbliklər."""
    files = {
        "main.py": "from utils import f\ndef run(): return f(10)",
        "utils.py": """
def f(x):
    if x > 0:
        if x > 10:
            return "big"
        return "small"
    return "zero"
""",
        "helpers.py": "def safe(x): return x or 0",
        "config.py": "DEBUG = True",
    }
    
    ctx = orch.process_pr(pr_number=42, repo="test/repo", files=files)
    
    assert len(ctx.ast_results) == 4
    assert ctx.graph_analysis is not None
    assert len(ctx.review_order) > 0
    assert len(ctx.errors) == 0


def test_cycle_detection_in_pipeline(orch):
    """Cycle olan layihə pipeline-də tutulur."""
    files = {
        "a.py": "from b import x",
        "b.py": "from a import y",
    }
    
    ctx = orch.process_pr(pr_number=1, repo="test/repo", files=files)
    
    assert ctx.graph_analysis.has_cycles is True


def test_priority_uses_complexity(orch):
    """Daha mürəkkəb fayl prioritetdə əvvəl gəlir."""
    files = {
        "simple.py": "x = 1",
        "medium.py": "def f(x):\n    if x: return 1\n    return 0",
        "complex.py": """
def f(x):
    if x > 0:
        if x > 10:
            for i in range(x):
                if i % 2 == 0:
                    pass
                else:
                    pass
        return 1
    elif x < 0:
        return -1
    return 0
""",
    }
    
    ctx = orch.process_pr(pr_number=1, repo="test/repo", files=files)
    
    assert ctx.review_order[0].filename == "complex.py"


def test_cache_persistence_across_prs(orch):
    """Cache PR-lər arasında qalır."""
    code = "def helper(): return 42"
    files = {"helper.py": code}
    
    ctx1 = orch.process_pr(pr_number=1, repo="test/repo", files=files)
    assert "helper.py" in ctx1.files_to_review
    
    orch.cache.set(code, {"summary": "good"})
    
    ctx2 = orch.process_pr(pr_number=2, repo="test/repo", files=files)
    assert "helper.py" in ctx2.cached_files


def test_mixed_valid_and_broken(orch):
    """Valid və broken fayllar bir yerdə."""
    files = {
        "good.py": "def f(): return 1",
        "broken.py": "def g(:\n    pass",
        "another.py": "x = 1",
    }
    
    ctx = orch.process_pr(pr_number=1, repo="test/repo", files=files)
    
    assert len(ctx.errors) >= 1
    assert "good.py" in ctx.ast_results
    assert "another.py" in ctx.ast_results