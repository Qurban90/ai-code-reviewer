"""Post review comments to GitHub PRs."""
import os
import logging
from typing import Optional
from github import Github, GithubException
from src.reviewer.models import FileReview, ReviewIssue

logger = logging.getLogger(__name__)

SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🔵",
    "info": "💡",
}


class CommentPoster:
    """Posts AI review results as GitHub PR comments."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not set")
        self.gh = Github(self.token)

    def post_review(self, repo_name: str, pr_number: int, reviews: dict[str, FileReview]) -> dict:
        """Post all reviews to a PR."""
        try:
            repo = self.gh.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
        except GithubException as e:
            logger.error(f"GitHub error: {e}")
            return {"status": "error", "message": str(e)}

        inline_count = 0
        errors = []

        commit = pr.get_commits().reversed[0]

        for filename, review in reviews.items():
            for issue in review.issues:
                try:
                    body = self._format_inline_comment(issue)
                    pr.create_review_comment(
                        body=body,
                        commit=commit,
                        path=filename,
                        line=issue.line,
                    )
                    inline_count += 1
                except GithubException as e:
                    errors.append(f"{filename}:{issue.line} — {e.data.get('message', str(e))}")
                    logger.warning(f"Inline comment failed: {e}")

        summary = self._format_summary(reviews)
        try:
            pr.create_issue_comment(summary)
        except GithubException as e:
            errors.append(f"Summary comment failed: {e}")

        return {
            "status": "posted",
            "inline_comments": inline_count,
            "summary_posted": True,
            "errors": errors,
        }

    def _format_inline_comment(self, issue: ReviewIssue) -> str:
        emoji = SEVERITY_EMOJI.get(issue.severity, "⚪")
        lines = [
            f"{emoji} **{issue.severity.upper()}** — {issue.category}",
            f"\n{issue.message}",
        ]
        if issue.suggestion:
            lines.append(f"\n**Suggestion:** {issue.suggestion}")
        return "\n".join(lines)

    def _format_summary(self, reviews: dict[str, FileReview]) -> str:
        total_issues = sum(len(r.issues) for r in reviews.values())
        total_critical = sum(
            1 for r in reviews.values() for i in r.issues if i.severity == "critical"
        )

        lines = ["## 🤖 AI Code Review Summary\n"]

        for filename, review in reviews.items():
            score_bar = "🟢" if review.overall_score >= 7 else "🟡" if review.overall_score >= 4 else "🔴"
            lines.append(f"### {score_bar} `{filename}` — {review.overall_score}/10")
            lines.append(f"> {review.summary}\n")

            if review.issues:
                counts = review.issue_count_by_severity()
                parts = []
                for sev in ["critical", "high", "medium", "low", "info"]:
                    if counts[sev] > 0:
                        parts.append(f"{SEVERITY_EMOJI[sev]} {sev}: {counts[sev]}")
                lines.append(" | ".join(parts))
            else:
                lines.append("✅ No issues found")
            lines.append("")

        lines.append("---")
        lines.append(f"**Total:** {total_issues} issues across {len(reviews)} files")
        if total_critical > 0:
            lines.append(f"\n🔴 **{total_critical} critical issue(s) require immediate attention**")
        lines.append("\n*Powered by AI Code Reviewer*")

        return "\n".join(lines)