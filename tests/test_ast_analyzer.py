"""Unit tests for AST analyzer."""
import pytest
from src.parsers.ast_analyzer import ASTAnalyzer


@pytest.fixture
def analyzer():
    return ASTAnalyzer()


def test_simple_function(analyzer):
    """Sadə funksiya düzgün parse olunur."""
    code = "def hello(): return 'world'"
    result = analyzer.analyze(code)
    
    assert len(result.functions) == 1
    assert result.functions[0].name == "hello"
    assert result.functions[0].complexity == 1
    assert not result.has_syntax_error


def test_function_with_args(analyzer):
    """Argümentli funksiya."""
    code = "def add(a, b, c): return a + b + c"
    result = analyzer.analyze(code)
    
    assert result.functions[0].args == ["a", "b", "c"]


def test_complexity_calculation(analyzer):
    """Cyclomatic complexity düzgün hesablanır."""
    code = """
def check(x):
    if x > 0:
        if x > 10:
            return "big"
        return "small"
    elif x < 0:
        return "negative"
    return "zero"
"""
    result = analyzer.analyze(code)
    # 1 (base) + 3 if + 1 elif = 4
    assert result.functions[0].complexity == 4


def test_class_detection(analyzer):
    """Class-lar düzgün tapılır."""
    code = """
class MyClass(BaseClass):
    def method1(self): pass
    def method2(self): pass
"""
    result = analyzer.analyze(code)
    
    assert len(result.classes) == 1
    assert result.classes[0].name == "MyClass"
    assert "method1" in result.classes[0].methods
    assert "method2" in result.classes[0].methods


def test_imports(analyzer):
    """Import-lar düzgün tutulur."""
    code = """
import os
import sys as system
from typing import List, Dict
"""
    result = analyzer.analyze(code)
    
    assert len(result.imports) == 3
    # Birinci: import os
    assert result.imports[0].module == "os"
    assert not result.imports[0].is_from_import
    # Üçüncü: from typing import List, Dict
    assert result.imports[2].module == "typing"
    assert result.imports[2].is_from_import
    assert "List" in result.imports[2].names
    assert "Dict" in result.imports[2].names


def test_async_function(analyzer):
    """Async funksiya tanınır."""
    code = "async def fetch(): return 42"
    result = analyzer.analyze(code)
    
    assert result.functions[0].is_async is True


def test_syntax_error(analyzer):
    """Sintaksis xətası tutulur."""
    code = "def broken(:\n    pass"  # qəsdən pozulub
    result = analyzer.analyze(code)
    
    assert result.has_syntax_error is True
    assert result.error_message is not None


def test_empty_file(analyzer):
    """Boş fayl çökmür."""
    result = analyzer.analyze("")
    
    assert len(result.functions) == 0
    assert len(result.classes) == 0
    assert not result.has_syntax_error


def test_avg_complexity(analyzer):
    """Orta mürəkkəblik hesablanır."""
    code = """
def f1(): return 1
def f2():
    if True: return 1
    return 2
"""
    result = analyzer.analyze(code)
    # f1: 1, f2: 2 → orta 1.5
    assert result.avg_complexity == 1.5