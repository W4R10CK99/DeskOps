"""Deterministic filtering, sorting, and bounded pagination helpers."""

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")


def page_items(
    records: Sequence[T],
    *,
    key: Callable[[T], object],
    descending: bool,
    offset: int,
    limit: int,
) -> tuple[list[T], int]:
    ordered = sorted(records, key=key, reverse=descending)
    return ordered[offset : offset + limit], len(ordered)
