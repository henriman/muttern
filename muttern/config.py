from typing import Callable, Any

def str_to_tuple(s: str, f: Callable[[str], Any]):
    return tuple(map(f, s.strip("()").split(", ")))
