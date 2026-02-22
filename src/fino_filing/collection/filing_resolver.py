"""
Filing 具象クラス解決（保存時のクラスで復元するためのレジストリ）

責務:
- 完全修飾クラス名と Filing サブクラスのマッピングを保持
- get/find 時に _filing_class から復元に使うクラスを解決する
"""
from __future__ import annotations

from fino_filing.filing.filing import Filing

_REGISTRY: dict[str, type[Filing]] = {}


def register_filing_class(name: str, cls: type[Filing]) -> None:
    """
    完全修飾クラス名で Filing サブクラスを登録する。
    get_filing / find でそのクラスとして復元する際に利用する。

    Args:
        name: 完全修飾名（例: fino_filing.filing.filing_edinet.EDINETFiling）
        cls: 登録する Filing サブクラス
    """
    _REGISTRY[name] = cls


def resolve_filing_class(name: str | None) -> type[Filing] | None:
    """
    完全修飾クラス名から Filing サブクラスを解決する。

    Args:
        name: 保存時に付与した _filing_class の値。None または未登録の場合は None を返す。

    Returns:
        登録されていればそのクラス、そうでなければ None（呼び出し側で Filing に fallback する）
    """
    if not name:
        return None
    return _REGISTRY.get(name)
