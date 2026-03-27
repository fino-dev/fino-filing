"""Edinet 用共有ヘルパー。Collector から利用する。"""

from __future__ import annotations

from datetime import date, datetime


def _parse_edinet_date(s: str | None) -> date | None:
    """
    EDinet date string (YYYY-MM-DD) to date.
    If the string is not in the correct format, return None.
    """
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _parse_edinet_datetime(s: str | None) -> datetime | None:
    """
    EDinet datetime string (YYYY-MM-DD HH:MM) to datetime.
    If the string is not in the correct format, return None.
    """
    if not s:
        return None
    try:
        # マイクロ秒付き / タイムゾーン付きにも対応するため [:26] で切り捨て
        return datetime.fromisoformat(s.replace("Z", "+00:00")[:26])
    except (ValueError, TypeError):
        return None
