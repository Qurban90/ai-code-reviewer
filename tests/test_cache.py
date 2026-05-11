"""Tests for review cache."""
import pytest
import tempfile
from pathlib import Path
from src.cache.review_cache import ReviewCache


@pytest.fixture
def cache(tmp_path):
    return ReviewCache(cache_dir=str(tmp_path / "cache"))


def test_empty_cache(cache):
    assert cache.size() == 0
    assert cache.get("code") is None


def test_set_and_get(cache):
    code = "def hello(): pass"
    review = {"summary": "ok"}
    cache.set(code, review)
    
    result = cache.get(code)
    assert result is not None
    assert result.review_data == review


def test_has(cache):
    code = "x = 1"
    assert cache.has(code) is False
    cache.set(code, {})
    assert cache.has(code) is True


def test_different_code_different_hash(cache):
    cache.set("code1", {"a": 1})
    cache.set("code2", {"b": 2})
    
    assert cache.size() == 2
    assert cache.get("code1").review_data == {"a": 1}
    assert cache.get("code2").review_data == {"b": 2}


def test_same_code_same_hash(cache):
    cache.set("identical", {"v": 1})
    cache.set("identical", {"v": 2})
    
    assert cache.size() == 1
    assert cache.get("identical").review_data == {"v": 2}


def test_clear(cache):
    cache.set("a", {})
    cache.set("b", {})
    cache.clear()
    
    assert cache.size() == 0


def test_persistence(tmp_path):
    cache_dir = str(tmp_path / "persist")
    
    cache1 = ReviewCache(cache_dir=cache_dir)
    cache1.set("code", {"x": 42})
    
    cache2 = ReviewCache(cache_dir=cache_dir)
    result = cache2.get("code")
    
    assert result is not None
    assert result.review_data == {"x": 42}


def test_stats(cache):
    cache.set("a", {})
    cache.set("b", {})
    stats = cache.stats()
    
    assert stats["entries"] == 2
    assert "cache_dir" in stats