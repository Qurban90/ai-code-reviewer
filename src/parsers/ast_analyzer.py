"""
AST Analyzer — Python kodunun strukturunu çıxaran modul.

Bu modul Python faylını Abstract Syntax Tree-yə çevirir və 
hər funksiya, class, import haqqında məlumat çıxarır.

DSA Konsepti: Tree (Abstract Syntax Tree)
- Hər node bir kod elementidir (funksiya, if, return, və s.)
- Traversal: ast.walk() ilə bütün node-ları gəzirik
- Big-O: O(n) — burada n = node sayı
"""
import ast
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FunctionInfo:
    """Bir funksiya haqqında məlumat."""
    name: str
    line_start: int
    line_end: int
    args: List[str] = field(default_factory=list)
    complexity: int = 1
    docstring: Optional[str] = None
    is_async: bool = False


@dataclass
class ClassInfo:
    """Bir class haqqında məlumat."""
    name: str
    line_start: int
    line_end: int
    methods: List[str] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class ImportInfo:
    """Bir import haqqında məlumat."""
    module: str
    names: List[str] = field(default_factory=list)
    line: int = 0
    is_from_import: bool = False


@dataclass
class FileAnalysis:
    """Bütün fayl üçün analiz nəticəsi."""
    filename: str
    functions: List[FunctionInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    total_lines: int = 0
    avg_complexity: float = 0.0
    has_syntax_error: bool = False
    error_message: Optional[str] = None


class ASTAnalyzer:
    """Python kodunu AST formatında analiz edir."""
    
    def analyze(self, code: str, filename: str = "<unknown>") -> FileAnalysis:
        """
        Verilmiş Python kodunu analiz edir.
        
        Args:
            code: Python kodu (string)
            filename: Fayl adı (loqlar üçün)
        
        Returns:
            FileAnalysis: Tam analiz nəticəsi
        """
        result = FileAnalysis(
            filename=filename,
            total_lines=len(code.splitlines()),
        )
        
        # Sintaksis xətasını tut
        try:
            tree = ast.parse(code, filename=filename)
        except SyntaxError as e:
            result.has_syntax_error = True
            result.error_message = f"Line {e.lineno}: {e.msg}"
            return result
        
        # Tree-ni gəz, məlumat topla
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                result.functions.append(self._analyze_function(node))
            elif isinstance(node, ast.ClassDef):
                result.classes.append(self._analyze_class(node))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result.imports.append(ImportInfo(
                        module=alias.name,
                        names=[alias.asname or alias.name],
                        line=node.lineno,
                        is_from_import=False,
                    ))
            elif isinstance(node, ast.ImportFrom):
                result.imports.append(ImportInfo(
                    module=node.module or "",
                    names=[alias.name for alias in node.names],
                    line=node.lineno,
                    is_from_import=True,
                ))
        
        # Orta mürəkkəbliyi hesabla
        if result.functions:
            total = sum(f.complexity for f in result.functions)
            result.avg_complexity = round(total / len(result.functions), 2)
        
        return result
    
    def _analyze_function(self, node) -> FunctionInfo:
        """Bir funksiya node-undan məlumat çıxar."""
        return FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            args=[arg.arg for arg in node.args.args],
            complexity=self._calculate_complexity(node),
            docstring=ast.get_docstring(node),
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )
    
    def _analyze_class(self, node: ast.ClassDef) -> ClassInfo:
        """Bir class node-undan məlumat çıxar."""
        methods = [
            n.name for n in node.body 
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        bases = [
            ast.unparse(b) if hasattr(ast, 'unparse') else str(b)
            for b in node.bases
        ]
        return ClassInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            methods=methods,
            base_classes=bases,
            docstring=ast.get_docstring(node),
        )
    
    def _calculate_complexity(self, node) -> int:
        """
        Cyclomatic complexity hesabla.
        
        Düstur: 1 + decision point sayı
        Decision points: if, elif, for, while, except, and, or, ternary
        
        Niyə: kodun nə qədər çətin oxunduğunu ölçür.
        - 1-5: sadə, asan oxunur
        - 6-10: orta
        - 11+: mürəkkəb, refactor lazım ola bilər
        """
        complexity = 1  # base path
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # 'and'/'or' hər biri əlavə branch
                complexity += len(child.values) - 1
            elif isinstance(child, ast.IfExp):
                # ternary: x if cond else y
                complexity += 1
        
        return complexity