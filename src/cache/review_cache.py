"""
Review Cache — eyni kodu iki dəfə review etməmək üçün hash map.

DSA: Hash Map (dict)
Time: get/set O(1) ortalama
"""
import hashlib
import json
import os
import pickle
from dataclasses import dataclass, asdict
from typing import Any, Optional
from pathlib import Path


@dataclass
class CachedReview:
    file_hash: str
    review_data: dict
    created_at: str


class ReviewCache:
    """Hash-əsaslı review cache (in-memory + disk)."""
    
    def __init__(self, cache_dir: str = "review_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory: dict[str, CachedReview] = {}
        self._load_from_disk()
    
    def get(self, code: str) -> Optional[CachedReview]:
        h = self._hash(code)
        return self._memory.get(h)
    
    def set(self, code: str, review_data: dict) -> str:
        from datetime import datetime
        h = self._hash(code)
        entry = CachedReview(
            file_hash=h,
            review_data=review_data,
            created_at=datetime.now().isoformat(),
        )
        self._memory[h] = entry
        self._save_to_disk(h, entry)
        return h
    
    def has(self, code: str) -> bool:
        return self._hash(code) in self._memory
    
    def clear(self) -> None:
        self._memory.clear()
        for f in self.cache_dir.glob("*.pkl"):
            f.unlink()
    
    def size(self) -> int:
        return len(self._memory)
    
    def stats(self) -> dict:
        return {
            "entries": len(self._memory),
            "cache_dir": str(self.cache_dir),
            "disk_files": len(list(self.cache_dir.glob("*.pkl"))),
        }
    
    def _hash(self, code: str) -> str:
        return hashlib.sha256(code.encode("utf-8")).hexdigest()
    
    def _save_to_disk(self, h: str, entry: CachedReview) -> None:
        path = self.cache_dir / f"{h}.pkl"
        with open(path, "wb") as f:
            pickle.dump(entry, f)
    
    def _load_from_disk(self) -> None:
        for f in self.cache_dir.glob("*.pkl"):
            try:
                with open(f, "rb") as fp:
                    entry: CachedReview = pickle.load(fp)
                    self._memory[entry.file_hash] = entry
            except Exception:
                continue