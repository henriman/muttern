"""This module includes helper functions for the config parser."""

from typing import Callable, Any, TypeVar, Tuple

T = TypeVar("T")

def str_to_tuple(s: str, t: Callable[[str], T]) -> Tuple[T, ...]:
    """Parse a string into a tuple of type `t`."""

    return tuple(map(t, s.strip("()").split(", ")))

# TODO: product.py: self.lc as class variable?
