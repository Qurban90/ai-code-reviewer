"""Unit tests for dependency graph builder."""
import pytest
from src.graph.dependency_graph import DependencyGraphBuilder


@pytest.fixture
def builder():
    return DependencyGraphBuilder()


def test_simple_graph(builder):
    """İki fayllı sadə qraf."""
    files = {
        "a.py": "from b import something",
        "b.py": "x = 1",
    }
    graph = builder.build_from_files(files)
    
    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 1
    assert graph.has_edge("a", "b")


def test_no_imports(builder):
    """Heç bir import olmayan fayllar."""
    files = {
        "a.py": "x = 1",
        "b.py": "y = 2",
    }
    graph = builder.build_from_files(files)
    
    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 0


def test_cycle_detection(builder):
    """Cycle düzgün tutulur."""
    files = {
        "a.py": "from b import x",
        "b.py": "from a import y",
    }
    builder.build_from_files(files)
    analysis = builder.analyze()
    
    assert analysis.has_cycles is True
    assert len(analysis.cycles) >= 1


def test_no_cycle(builder):
    """Cycle olmayan qraf."""
    files = {
        "a.py": "from b import x",
        "b.py": "from c import y",
        "c.py": "z = 1",
    }
    builder.build_from_files(files)
    analysis = builder.analyze()
    
    assert analysis.has_cycles is False


def test_external_imports_ignored(builder):
    """Xarici kitabxanalar qrafa daxil edilmir."""
    files = {
        "a.py": "import os\nimport sys\nfrom b import x",
        "b.py": "z = 1",
    }
    graph = builder.build_from_files(files)
    
    # `os` və `sys` xaricidir, daxil edilməməlidir
    assert "os" not in graph.nodes()
    assert "sys" not in graph.nodes()
    assert graph.number_of_edges() == 1


def test_impact_analysis(builder):
    """Impact analysis düzgün işləyir."""
    files = {
        "main.py": "from utils import f\nfrom db import g",
        "utils.py": "from helpers import h",
        "db.py": "from models import M",
        "helpers.py": "x = 1",
        "models.py": "y = 1",
    }
    builder.build_from_files(files)
    
    # `helpers` dəyişərsə → `utils`, `main` təsirlənir
    impact = builder.get_impact("helpers")
    assert "utils" in impact
    assert "main" in impact
    assert "db" not in impact  # db-nin helpers-lə əlaqəsi yoxdur


def test_dependencies(builder):
    """Dependencies düzgün tapılır."""
    files = {
        "main.py": "from utils import f",
        "utils.py": "from helpers import h",
        "helpers.py": "x = 1",
    }
    builder.build_from_files(files)
    
    # main → utils → helpers
    deps = builder.get_dependencies("main")
    assert "utils" in deps
    assert "helpers" in deps


def test_isolated_files(builder):
    """İzolyasiya olunmuş fayllar tapılır."""
    files = {
        "a.py": "from b import x",
        "b.py": "y = 1",
        "lonely.py": "z = 1",
    }
    builder.build_from_files(files)
    analysis = builder.analyze()
    
    assert "lonely" in analysis.isolated_files


def test_empty_project(builder):
    """Boş layihə çökmür."""
    graph = builder.build_from_files({})
    analysis = builder.analyze()
    
    assert analysis.total_files == 0
    assert analysis.total_imports == 0
    assert analysis.has_cycles is False


def test_syntax_error_handled(builder):
    """Sintaksis xətası olan fayllar çökdürmür."""
    files = {
        "good.py": "from bad import x",
        "bad.py": "def broken(:\n    pass",  # qəsdən pozulub
    }
    # Çökməməlidir
    graph = builder.build_from_files(files)
    assert graph.number_of_nodes() == 2