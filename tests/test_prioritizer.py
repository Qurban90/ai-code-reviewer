"""Tests for priority queue."""
import pytest
from src.priority.prioritizer import ReviewPrioritizer, FileMetrics


@pytest.fixture
def pq():
    return ReviewPrioritizer()


def test_empty(pq):
    assert pq.size() == 0
    assert pq.pop_top() is None


def test_single_add(pq):
    pq.add(FileMetrics("a.py", complexity=5))
    assert pq.size() == 1


def test_high_complexity_first(pq):
    pq.add(FileMetrics("simple.py", complexity=1, dependencies=0, lines_changed=5))
    pq.add(FileMetrics("complex.py", complexity=15, dependencies=10, lines_changed=200))
    
    top = pq.pop_top()
    assert top.filename == "complex.py"


def test_top_n_order(pq):
    pq.add(FileMetrics("low.py", complexity=1))
    pq.add(FileMetrics("high.py", complexity=20))
    pq.add(FileMetrics("mid.py", complexity=10))
    
    top = pq.top_n(3)
    assert top[0].filename == "high.py"
    assert top[1].filename == "mid.py"
    assert top[2].filename == "low.py"


def test_dependencies_factor(pq):
    pq.add(FileMetrics("a.py", complexity=5, dependencies=0))
    pq.add(FileMetrics("b.py", complexity=5, dependencies=10))
    
    top = pq.pop_top()
    assert top.filename == "b.py"


def test_lines_factor(pq):
    pq.add(FileMetrics("a.py", complexity=5, lines_changed=0))
    pq.add(FileMetrics("b.py", complexity=5, lines_changed=500))
    
    top = pq.pop_top()
    assert top.filename == "b.py"


def test_size_decreases(pq):
    pq.add(FileMetrics("a.py", complexity=1))
    pq.add(FileMetrics("b.py", complexity=2))
    
    pq.pop_top()
    assert pq.size() == 1


def test_top_n_larger_than_size(pq):
    pq.add(FileMetrics("a.py", complexity=1))
    top = pq.top_n(10)
    assert len(top) == 1