"""End-to-end tests — full pipeline without real GitHub/Claude."""
import pytest
from unittest.mock import MagicMock, patch
import json
from src.orchestrator import ReviewOrchestrator
from src.reviewer.models import FileReview, ReviewIssue


@pytest.fixture
def orch_with_mock_ai(tmp_path):
    """Orchestrator with mocked Claude."""
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test", "GITHUB_TOKEN": "test"}):
        orch = ReviewOrchestrator(
            cache_dir=str(tmp_path / "cache"),
            max_files=5,
            enable_ai=True,
        )

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "filename": "test.py",
        "issues": [
            {"line": 1, "severity": "high", "category": "bug",
             "message": "Issue found", "suggestion": "Fix it"}
        ],
        "summary": "Has issues",
        "overall_score": 5,
    }))]

    if orch.claude:
        orch.claude.client.messages.create = MagicMock(return_value=mock_response)

    orch.poster = None  # Disable posting

    return orch


def test_full_pipeline_buggy_code(orch_with_mock_ai):
    """Buggy kod tam pipeline-dən keçir."""
    files = {
        "auth.py": '''
SECRET_KEY = "supersecret123"

def hash_password(password):
    import hashlib
    return hashlib.md5(password.encode()).hexdigest()

def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}'"
    return query
''',
    }

    ctx = orch_with_mock_ai.process_pr(
        pr_number=1, repo="test/repo", files=files,
        changed_lines={"auth.py": 50},
    )

    assert "auth.py" in ctx.ast_results
    assert len(ctx.review_order) == 1
    assert "auth.py" in ctx.reviews
    assert ctx.reviews["auth.py"].overall_score > 0


def test_full_pipeline_clean_code(orch_with_mock_ai):
    """Təmiz kod pipeline-dən keçir."""
    files = {
        "calc.py": '''
def add(a: int, b: int) -> int:
    return a + b

def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Zero division")
    return a / b
''',
    }

    ctx = orch_with_mock_ai.process_pr(
        pr_number=2, repo="test/repo", files=files,
    )

    assert "calc.py" in ctx.ast_results
    assert len(ctx.errors) == 0


def test_full_pipeline_mixed_files(orch_with_mock_ai):
    """Python + non-Python fayllar birlikdə."""
    files = {
        "app.py": "def main(): pass",
        "README.md": "# Hello",
        "config.json": "{}",
        "broken.py": "def f(:\n    pass",
    }

    ctx = orch_with_mock_ai.process_pr(
        pr_number=3, repo="test/repo", files=files,
    )

    assert "app.py" in ctx.ast_results
    assert "README.md" not in ctx.ast_results
    assert len(ctx.errors) >= 1  # broken.py


def test_full_pipeline_empty_pr(orch_with_mock_ai):
    """Boş PR çökmür."""
    ctx = orch_with_mock_ai.process_pr(
        pr_number=4, repo="test/repo", files={},
    )
    assert len(ctx.ast_results) == 0
    assert len(ctx.reviews) == 0


def test_full_pipeline_large_pr(orch_with_mock_ai):
    """Çox fayllı PR — max_files limit işləyir."""
    files = {f"file{i}.py": f"def f{i}(): return {i}" for i in range(20)}

    ctx = orch_with_mock_ai.process_pr(
        pr_number=5, repo="test/repo", files=files,
    )

    assert len(ctx.review_order) == 5  # max_files=5


def test_cache_prevents_duplicate_review(orch_with_mock_ai):
    """Cache eyni kodu iki dəfə review etmir."""
    code = "def f(): return 42"
    files = {"a.py": code}

    ctx1 = orch_with_mock_ai.process_pr(pr_number=1, repo="test/repo", files=files)
    call_count_1 = orch_with_mock_ai.claude.client.messages.create.call_count

    ctx2 = orch_with_mock_ai.process_pr(pr_number=2, repo="test/repo", files=files)
    call_count_2 = orch_with_mock_ai.claude.client.messages.create.call_count

    assert call_count_2 == call_count_1  # İkinci PR-da API çağırılmır


def test_syntax_error_still_reviewed(orch_with_mock_ai):
    """Syntax error olan faylda AST error qeyd olunur amma pipeline davam edir."""
    files = {
        "good.py": "def f(): return 1",
        "bad.py": "def g(:\n    pass",
    }

    ctx = orch_with_mock_ai.process_pr(
        pr_number=6, repo="test/repo", files=files,
    )

    assert "good.py" in ctx.ast_results
    assert len(ctx.errors) >= 1
    assert any("bad.py" in e for e in ctx.errors)