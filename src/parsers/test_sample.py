"""Sample Python file for testing AST analyzer."""
import os
import sys
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class User:
    """A user in the system."""
    name: str
    age: int
    
    def greet(self) -> str:
        """Return a greeting."""
        return f"Hello, {self.name}!"


def simple_function(x: int) -> int:
    """Just returns x doubled."""
    return x * 2


def complex_function(items: List[int]) -> Dict[str, int]:
    """A more complex function with high cyclomatic complexity."""
    result = {"positive": 0, "negative": 0, "zero": 0}
    
    for item in items:
        if item > 0:
            if item > 100:
                result["positive"] += 2
            else:
                result["positive"] += 1
        elif item < 0:
            result["negative"] += 1
        else:
            result["zero"] += 1
    
    try:
        ratio = result["positive"] / result["negative"]
    except ZeroDivisionError:
        ratio = 0
    
    return result


async def fetch_data(url: str) -> str:
    """Async function example."""
    return "data"