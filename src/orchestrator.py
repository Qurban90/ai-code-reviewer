"""
Orchestrator — bütün modulları birləşdirən mərkəzi koordinator.

Axın: PR fayllar → AST analiz → Graph → Priority → Cache → [AI] → Log
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.parsers.ast_analyzer import ASTAnalyzer, FileAnalysis
from src.graph.dependency_graph import DependencyGraphBuilder, GraphAnalysis
from src.priority.prioritizer import ReviewPrioritizer, FileMetrics, PrioritizedFile
from src.cache.review_cache import ReviewCache


logger = logging.getLogger(__name__)


@dataclass
class PRReviewContext:
    """Bir PR üçün tam analiz konteksti."""
    pr_number: int
    repo: str
    files: Dict[str, str] = field(default_factory=dict)  # {filename: code}
    files_changed_lines: Dict[str, int] = field(default_factory=dict)
    
    ast_results: Dict[str, FileAnalysis] = field(default_factory=dict)
    graph_analysis: Optional[GraphAnalysis] = None
    review_order: List[PrioritizedFile] = field(default_factory=list)
    cached_files: List[str] = field(default_factory=list)
    files_to_review: List[str] = field(default_factory=list)
    
    errors: List[str] = field(default_factory=list)


class ReviewOrchestrator:
    """PR review pipeline-ı idarə edir."""
    
    def __init__(self, cache_dir: str = "review_cache", max_files: int = 5):
        self.ast_analyzer = ASTAnalyzer()
        self.graph_builder = DependencyGraphBuilder()
        self.cache = ReviewCache(cache_dir=cache_dir)
        self.max_files = max_files
    
    def process_pr(
        self,
        pr_number: int,
        repo: str,
        files: Dict[str, str],
        changed_lines: Optional[Dict[str, int]] = None,
    ) -> PRReviewContext:
        """PR-ı tam pipeline-dən keçirir."""
        ctx = PRReviewContext(
            pr_number=pr_number,
            repo=repo,
            files=files,
            files_changed_lines=changed_lines or {},
        )
        
        logger.info(f"Processing PR #{pr_number} from {repo}")
        logger.info(f"Files in PR: {len(files)}")
        
        self._step_ast(ctx)
        self._step_graph(ctx)
        self._step_priority(ctx)
        self._step_cache_filter(ctx)
        
        return ctx
    
    def _step_ast(self, ctx: PRReviewContext) -> None:
        """Mərhələ 1: hər faylı AST ilə analiz et."""
        logger.info("Step 1: AST analysis")
        
        for filename, code in ctx.files.items():
            if not filename.endswith(".py"):
                continue
            try:
                analysis = self.ast_analyzer.analyze(code, filename)
                ctx.ast_results[filename] = analysis
                if analysis.has_syntax_error:
                    ctx.errors.append(f"{filename}: {analysis.error_message}")
            except Exception as e:
                ctx.errors.append(f"AST error in {filename}: {e}")
    
    def _step_graph(self, ctx: PRReviewContext) -> None:
        """Mərhələ 2: dependency graph qur."""
        logger.info("Step 2: Dependency graph")
        
        try:
            py_files = {f: c for f, c in ctx.files.items() if f.endswith(".py")}
            self.graph_builder.build_from_files(py_files)
            ctx.graph_analysis = self.graph_builder.analyze()
        except Exception as e:
            ctx.errors.append(f"Graph error: {e}")
    
    def _step_priority(self, ctx: PRReviewContext) -> None:
        """Mərhələ 3: priority queue qur."""
        logger.info("Step 3: Priority ranking")
        
        pq = ReviewPrioritizer()
        
        for filename, ast_result in ctx.ast_results.items():
            if ast_result.has_syntax_error:
                continue
            
            complexity = max(
                (f.complexity for f in ast_result.functions),
                default=1,
            )
            
            module_name = filename.replace(".py", "").replace("/", ".")
            deps = 0
            if ctx.graph_analysis:
                try:
                    deps = len(self.graph_builder.get_impact(module_name))
                except Exception:
                    deps = 0
            
            lines_changed = ctx.files_changed_lines.get(filename, ast_result.total_lines)
            
            pq.add(FileMetrics(
                filename=filename,
                complexity=complexity,
                dependencies=deps,
                lines_changed=lines_changed,
            ))
        
        ctx.review_order = pq.top_n(self.max_files)
    
    def _step_cache_filter(self, ctx: PRReviewContext) -> None:
        """Mərhələ 4: cache yoxla, hansı fayllar yeniden review olunmalıdır."""
        logger.info("Step 4: Cache filter")
        
        for pf in ctx.review_order:
            code = ctx.files.get(pf.filename, "")
            if self.cache.has(code):
                ctx.cached_files.append(pf.filename)
            else:
                ctx.files_to_review.append(pf.filename)