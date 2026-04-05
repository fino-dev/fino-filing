"""Edgar 用共有ヘルパー。Config/Client/Collector から利用する。"""

from __future__ import annotations

from datetime import datetime
from typing import Any


# TODO: Collector refactorで不要であれば消す。テストみ作成
def _parse_edgar_date(s: str | None) -> datetime | None:
    """YYYY-MM-DD または None を datetime に変換する。"""
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _accession_to_dir(accession: str) -> str:
    """accession_number to Archives directory name"""
    return accession.replace("-", "")


def _filenames_from_sec_index_json(raw: dict[str, Any]) -> list[str]:
    """Get filenames relative path from SEC index.json"""
    directory = raw.get("directory")
    if not isinstance(directory, dict):
        return []
    item = directory.get("item")
    if item is None:
        return []
    if isinstance(item, dict):
        items: list[Any] = [item]
    elif isinstance(item, list):
        items = item
    else:
        return []
    out: list[str] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        name = it.get("name")
        if isinstance(name, str) and name.strip():
            out.append(name.strip())
    return out
