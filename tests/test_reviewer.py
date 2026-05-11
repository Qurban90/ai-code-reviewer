"""Tests for Claude reviewer."""
import pytest
import json
from unittest.mock import MagicMock, patch
from src.reviewer.claude_reviewer import ClaudeReviewer
from src.reviewer.models import FileReview, ReviewIssue


@pytest.fixture
def reviewer():
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        return ClaudeReviewer(api_key="test-key")


def test_init_without_key():
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}, clear=True):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            ClaudeReviewer(api_key="")


def test_parse_clean_json(reviewer):
    response = json.dumps({
        "filename": "a.py",
        "issues": [
            {"line": 1, "severity": "high", "category": "bug",
             "message": "Test", "suggestion": "Fix it"}
        ],
        "summary": "Has bug",
        "overall_score": 5,
    })
    
    result = reviewer._parse_response(response, "a.py")
    
    assert isinstance(result, FileReview)
    assert len(result.issues) == 1
    assert result.issues[0].line == 1
    assert result.overall_score == 5


def test_parse_markdown_wrapped_json(reviewer):
    response = '```json\n{"filename": "a.py", "issues": [], "summary": "ok", "overall_score": 8}\n```'
    
    result = reviewer._parse_response(response, "a.py")
    
    assert result.filename == "a.py"
    assert result.overall_score == 8


def test_parse_invalid_json(reviewer):
    response = "not valid json at all"
    result = reviewer._parse_response(response, "a.py")
    
    assert result.overall_score == 0
    assert "failed" in result.summary.lower()


def test_review_issue_validation():
    issue = ReviewIssue(
        line=10,
        severity="high",
        category="bug",
        message="test",
        suggestion="fix",
    )
    assert issue.line == 10


def test_invalid_severity_rejected():
    with pytest.raises(Exception):
        ReviewIssue(
            line=1,
            severity="super-bad",
            category="bug",
            message="x",
            suggestion="y",
        )


def test_has_critical():
    review = FileReview(
        filename="a.py",
        issues=[
            ReviewIssue(line=1, severity="low", category="style", message="x", suggestion="y"),
            ReviewIssue(line=2, severity="critical", category="bug", message="x", suggestion="y"),
        ],
    )
    assert review.has_critical() is True


def test_severity_counts():
    review = FileReview(
        filename="a.py",
        issues=[
            ReviewIssue(line=1, severity="high", category="bug", message="x", suggestion="y"),
            ReviewIssue(line=2, severity="high", category="bug", message="x", suggestion="y"),
            ReviewIssue(line=3, severity="low", category="style", message="x", suggestion="y"),
        ],
    )
    counts = review.issue_count_by_severity()
    assert counts["high"] == 2
    assert counts["low"] == 1
    assert counts["critical"] == 0


def test_cost_estimate(reviewer):
    cost = reviewer.estimate_cost("def f(): return 1")
    assert cost["estimated_input_tokens"] > 0
    assert cost["estimated_cost_usd"] > 0


def test_error_review(reviewer):
    result = reviewer._error_review("a.py", "Test error")
    assert result.overall_score == 0
    assert "Test error" in result.summary
    assert len(result.issues) == 0


def test_review_file_with_mock(reviewer):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=json.dumps({
        "filename": "test.py",
        "issues": [],
        "summary": "Looks good",
        "overall_score": 9,
    }))]
    
    reviewer.client.messages.create = MagicMock(return_value=mock_response)
    
    result = reviewer.review_file("test.py", "def f(): return 1")
    
    assert result.filename == "test.py"
    assert result.overall_score == 9