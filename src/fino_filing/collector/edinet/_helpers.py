"""Edinet 用共有ヘルパー。Collector から利用する。"""

from __future__ import annotations

from datetime import datetime


def _parse_edinet_datetime(s: str | None) -> datetime | None:
    """ISO 形式の日時文字列または None を datetime に変換する。"""
    if not s:
        return None
    try:
        # マイクロ秒付き / タイムゾーン付きにも対応するため [:26] で切り捨て
        return datetime.fromisoformat(s.replace("Z", "+00:00")[:26])
    except (ValueError, TypeError):
        return None
