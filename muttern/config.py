"""This module includes helper functions for the config parser."""

from typing import Callable, Any

def str_to_tuple(s: str, t: Callable[[str], Any]):
    """Parse a string into a tuple of type `t`."""

    return tuple(map(t, s.strip("()").split(", ")))

# TODO: type hint here
# TODO: product.py: self.lc as class variable?
