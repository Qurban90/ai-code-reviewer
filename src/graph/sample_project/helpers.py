"""Low-level helpers."""


def safe_str(x) -> str:
    return str(x) if x else "N/A"