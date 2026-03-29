"""Stable delimited keys for catalog search (multivalue fields)."""

from typing import Sequence


def normalize_delimited_multivalue(values: Sequence[str] | None) -> str:
    """
    Build a pipe-delimited, sorted key for membership queries via Expr.contains.

    Tokens are stripped, empty dropped, deduplicated, then sorted. The result is
    wrapped as ``a|b`` so ``contains("a|b")`` does not match ``FAAPL``.
    """

    if not values:
        return ""
    parts = sorted({s.strip() for s in values if (s or "").strip()})
    if not parts:
        return ""
    return "|".join(parts)
