"""Tests for orchestrator."""
import pytest
from src.orchestrator import ReviewOrchestrator


@pytest.fixture
def orch(tmp_path):
    return ReviewOrchestrator(cache_dir=str(tmp_path / "cache"), max_files=3)


def test_empty_pr(orch):
    ctx = orch.process_pr(pr_number=1, repo="test/repo", files={})
    assert len(ctx.ast_results) == 0
    assert len(ctx.review_order) == 0


def test_single_file(orch):
    files = {"a.py": "def f(): return 1"}
    ctx = orch.process_pr(pr_number=1, repo="test/repo", files=files)
    
    assert "a.py" in ctx.ast_results
    assert len(ctx.review_order) == 1


def test_non_python_ignored(orch):
    files = {"a.py": "x = 1", "readme.md": "# hi", "config.json": "{}"}
    ctx = orch.process_pr(pr_number=1, repo="test/repo", files=files)
    
    assert len(ctx.ast_results) == 1


def test_syntax_error_recorded(orch):
    files = {"broken.py": "def f(:\n    pass"}
    ctx = orch.process_pr(pr_number=1, repo="test/repo", files=files)
    
    assert len(ctx.errors) > 0


def test_max_files_limit(orch):
    files = {f"file{i}.py": f"def f{i}(): return {i}" for i in range(10)}
    ctx = orch.process_pr(pr_number=1, repo="test/repo", files=files)
    
    assert len(ctx.review_order) == 3


def test_cache_filter(orch):
    files = {"a.py": "def f(): return 1"}
    
    ctx1 = orch.process_pr(pr_number=1, repo="test/repo", files=files)
    assert "a.py" in ctx1.files_to_review
    
    orch.cache.set(files["a.py"], {"summary": "ok"})
    
    ctx2 = orch.process_pr(pr_number=2, repo="test/repo", files=files)
    assert "a.py" in ctx2.cached_files


def test_complex_file_higher_priority(orch):
    files = {
        "simple.py": "x = 1",
        "complex.py": "def f(x):\n" + "    if x: pass\n" * 10,
    }
    ctx = orch.process_pr(pr_number=1, repo="test/repo", files=files)
    
    assert ctx.review_order[0].filename == "complex.py"