"""Claude AI integration for code review."""
import os
import json
import logging
from typing import Optional
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError
from pydantic import ValidationError

from src.reviewer.models import FileReview
from src.reviewer.prompts import SYSTEM_PROMPT, REVIEW_PROMPT_TEMPLATE
from src.parsers.ast_analyzer import FileAnalysis


logger = logging.getLogger(__name__)


class ClaudeReviewer:
    """Reviews code using Claude API."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
        self.max_tokens = 2048
        self.max_retries = 3
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        self.client = Anthropic(api_key=self.api_key)
    
    def review_file(
        self,
        filename: str,
        code: str,
        ast_analysis: Optional[FileAnalysis] = None,
        dependencies: int = 0,
    ) -> FileReview:
        """Review a single file and return structured output."""
        prompt = self._build_prompt(filename, code, ast_analysis, dependencies)
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                )
                
                text = response.content[0].text
                return self._parse_response(text, filename)
            
            except RateLimitError as e:
                wait = 2 ** attempt
                logger.warning(f"Rate limited, retry in {wait}s ({attempt+1}/{self.max_retries})")
                import time
                time.sleep(wait)
            
            except (APIError, APIConnectionError) as e:
                logger.error(f"Claude API error (attempt {attempt+1}): {e}")
                if attempt == self.max_retries - 1:
                    return self._error_review(filename, str(e))
        
        return self._error_review(filename, "Max retries exceeded")
    
    def _build_prompt(
        self,
        filename: str,
        code: str,
        ast_analysis: Optional[FileAnalysis],
        dependencies: int,
    ) -> str:
        func_count = len(ast_analysis.functions) if ast_analysis else 0
        cls_count = len(ast_analysis.classes) if ast_analysis else 0
        avg_cmplx = ast_analysis.avg_complexity if ast_analysis else 0.0
        
        return REVIEW_PROMPT_TEMPLATE.format(
            filename=filename,
            func_count=func_count,
            cls_count=cls_count,
            avg_complexity=avg_cmplx,
            dependencies=dependencies,
            code=code,
        )
    
    def _parse_response(self, text: str, filename: str) -> FileReview:
        """Extract JSON from Claude response and validate."""
        text = text.strip()
        
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
        
        try:
            data = json.loads(text)
            return FileReview(**data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nRaw: {text[:300]}")
            return self._error_review(filename, "Invalid JSON from model")
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return self._error_review(filename, f"Invalid schema: {e}")
    
    def _error_review(self, filename: str, error_msg: str) -> FileReview:
     return FileReview(
        filename=filename,
        overall_score=0,  # minimum valid score
        summary=f"Review failed: {error_msg}",
        issues=[],
    )
    
    def estimate_cost(self, code: str) -> dict:
        """Rough token + cost estimate."""
        input_tokens = len(code) // 4 + 500
        output_tokens = 800
        
        haiku_input = 0.80 / 1_000_000
        haiku_output = 4.00 / 1_000_000
        
        cost = input_tokens * haiku_input + output_tokens * haiku_output
        
        return {
            "estimated_input_tokens": input_tokens,
            "estimated_output_tokens": output_tokens,
            "estimated_cost_usd": round(cost, 6),
        }