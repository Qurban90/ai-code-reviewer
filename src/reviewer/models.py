"""Pydantic models for review output."""
from typing import List, Literal
from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low", "info"]


class ReviewIssue(BaseModel):
    line: int = Field(..., description="Line number where issue occurs")
    severity: Severity
    category: str = Field(..., description="bug, security, performance, style, etc.")
    message: str = Field(..., description="Short description of the issue")
    suggestion: str = Field(default="", description="How to fix it")


class FileReview(BaseModel):
    filename: str
    issues: List[ReviewIssue] = Field(default_factory=list)
    summary: str = Field(default="")
    overall_score: int = Field(default=5, ge=0, le=10)
    
    def has_critical(self) -> bool:
        return any(i.severity == "critical" for i in self.issues)
    
    def issue_count_by_severity(self) -> dict:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for issue in self.issues:
            counts[issue.severity] += 1
        return counts