"""Tests for GitHub comment poster."""
import pytest
from unittest.mock import MagicMock, patch
from src.github_integration.comment_poster import CommentPoster, SEVERITY_EMOJI
from src.reviewer.models import FileReview, ReviewIssue


def test_init_without_token():
    with patch.dict("os.environ", {"GITHUB_TOKEN": ""}, clear=True):
        with pytest.raises(ValueError, match="GITHUB_TOKEN"):
            CommentPoster(token="")


def test_format_inline_comment():
    with patch.dict("os.environ", {"GITHUB_TOKEN": "fake"}):
        poster = CommentPoster(token="fake")

    issue = ReviewIssue(
        line=10,
        severity="high",
        category="bug",
        message="Division by zero possible",
        suggestion="Add a zero check",
    )

    result = poster._format_inline_comment(issue)

    assert "🟠" in result
    assert "HIGH" in result
    assert "Division by zero" in result
    assert "Add a zero check" in result


def test_format_summary():
    with patch.dict("os.environ", {"GITHUB_TOKEN": "fake"}):
        poster = CommentPoster(token="fake")

    reviews = {
        "a.py": FileReview(
            filename="a.py",
            issues=[
                ReviewIssue(line=1, severity="critical", category="bug", message="x", suggestion="y"),
                ReviewIssue(line=5, severity="low", category="style", message="x", suggestion="y"),
            ],
            summary="Has issues",
            overall_score=3,
        ),
        "b.py": FileReview(
            filename="b.py",
            issues=[],
            summary="Clean",
            overall_score=9,
        ),
    }

    result = poster._format_summary(reviews)

    assert "AI Code Review Summary" in result
    assert "a.py" in result
    assert "b.py" in result
    assert "3/10" in result
    assert "9/10" in result
    assert "critical" in result.lower()
    assert "No issues found" in result


def test_severity_emojis():
    assert SEVERITY_EMOJI["critical"] == "🔴"
    assert SEVERITY_EMOJI["high"] == "🟠"
    assert SEVERITY_EMOJI["info"] == "💡"


def test_format_summary_no_issues():
    with patch.dict("os.environ", {"GITHUB_TOKEN": "fake"}):
        poster = CommentPoster(token="fake")

    reviews = {
        "clean.py": FileReview(
            filename="clean.py",
            issues=[],
            summary="Perfect",
            overall_score=10,
        ),
    }

    result = poster._format_summary(reviews)
    assert "No issues found" in result
    assert "critical" not in result.lower() or "0" in result