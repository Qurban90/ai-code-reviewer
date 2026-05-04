"""Utility functions."""
from helpers import safe_str


def format_output(data) -> str:
    return f"Result: {safe_str(data)}"