"""
Priority Queue — faylları review prioritetinə görə sırala.

DSA: Min-Heap (heapq)
Time: insert O(log n), pop O(log n)
"""
import heapq
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(order=True)
class PrioritizedFile:
    priority: float
    filename: str = field(compare=False)
    complexity: int = field(compare=False, default=0)
    dependencies: int = field(compare=False, default=0)
    lines_changed: int = field(compare=False, default=0)


@dataclass
class FileMetrics:
    filename: str
    complexity: int = 1
    dependencies: int = 0
    lines_changed: int = 0


class ReviewPrioritizer:
    """Min-heap əsaslı prioritizer (kiçik priority = yüksək vaciblik)."""
    
    def __init__(self):
        self._heap: List[PrioritizedFile] = []
    
    def add(self, metrics: FileMetrics) -> None:
        priority = self._compute_priority(metrics)
        item = PrioritizedFile(
            priority=priority,
            filename=metrics.filename,
            complexity=metrics.complexity,
            dependencies=metrics.dependencies,
            lines_changed=metrics.lines_changed,
        )
        heapq.heappush(self._heap, item)
    
    def pop_top(self) -> Optional[PrioritizedFile]:
        if not self._heap:
            return None
        return heapq.heappop(self._heap)
    
    def top_n(self, n: int) -> List[PrioritizedFile]:
        result = []
        temp = self._heap.copy()
        for _ in range(min(n, len(temp))):
            result.append(heapq.heappop(temp))
        return result
    
    def size(self) -> int:
        return len(self._heap)
    
    def _compute_priority(self, m: FileMetrics) -> float:
        """
        Düstur: priority = -(complexity*2 + dependencies + lines_changed/10)
        Mənfi işarə: heap min-heap-dir, biz isə BÖYÜK score-u əvvəl istəyirik.
        """
        score = (m.complexity * 2) + m.dependencies + (m.lines_changed / 10)
        return -score