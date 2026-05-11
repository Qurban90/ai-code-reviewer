"""Edge case tests."""
import pytest
from src.orchestrator import ReviewOrchestrator
from src.parsers.ast_analyzer import ASTAnalyzer
from src.reviewer.models import FileReview


@pytest.fixture
def orch(tmp_path):
    return ReviewOrchestrator(
        cache_dir=str(tmp_path / "cache"), max_files=5, enable_ai=False,
    )


def test_empty_python_file(orch):
    ctx = orch.process_pr(1, "t/r", files={"empty.py": ""})
    assert "empty.py" in ctx.ast_results
    assert not ctx.ast_results["empty.py"].has_syntax_error


def test_only_comments(orch):
    ctx = orch.process_pr(1, "t/r", files={"comments.py": "# just a comment\n# another"})
    assert "comments.py" in ctx.ast_results


def test_unicode_code(orch):
    ctx = orch.process_pr(1, "t/r", files={"uni.py": 'x = "Azərbaycan 🇦🇿"'})
    assert not ctx.ast_results["uni.py"].has_syntax_error


def test_very_long_function():
    analyzer = ASTAnalyzer()
    code = "def f():\n" + "    x = 1\n" * 500
    result = analyzer.analyze(code)
    assert len(result.functions) == 1


def test_deeply_nested_code():
    analyzer = ASTAnalyzer()
    code = "def f():\n"
    for i in range(15):
        code += "    " * (i + 1) + "if True:\n"
    code += "    " * 16 + "pass\n"
    result = analyzer.analyze(code)
    assert result.functions[0].complexity >= 15


def test_no_python_files_in_pr(orch):
    ctx = orch.process_pr(1, "t/r", files={
        "README.md": "# hi",
        "data.json": "{}",
        "style.css": "body {}",
    })
    assert len(ctx.ast_results) == 0
    assert len(ctx.review_order) == 0


def test_duplicate_filenames(orch):
    ctx = orch.process_pr(1, "t/r", files={
        "utils.py": "x = 1",
        "utils.py": "x = 2",
    })
    assert ctx.ast_results["utils.py"].total_lines > 0


def test_file_review_model_defaults():
    review = FileReview(filename="test.py")
    assert review.overall_score == 5
    assert review.issues == []
    assert review.summary == ""
    assert review.has_critical() is False