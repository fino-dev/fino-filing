"""
Filing 具象クラス解決（保存時のクラスで復元するためのレジストリ）

責務:
- 完全修飾クラス名と Filing サブクラスのマッピングを保持
- get/find 時に _filing_class から復元に使うクラスを解決する
- 未登録の場合は完全修飾名から動的インポートで解決を試みる（ユーザー定義 Filing の UX 向上）
"""
from __future__ import annotations

import importlib
import logging
from functools import reduce
from typing import cast

from fino_filing.filing.filing import Filing

logger = logging.getLogger(__name__)

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


def _resolve_filing_class_by_import(name: str) -> type[Filing] | None:
    """
    完全修飾クラス名から importlib でクラスを取得する。
    取得したクラスは Filing のサブクラスであることを確認し、レジストリにキャッシュする。
    """
    parts = name.split(".")
    if len(parts) < 2:
        return None
    for i in range(1, len(parts)):
        module_path = ".".join(parts[:i])
        attr_path = ".".join(parts[i:])
        try:
            module = importlib.import_module(module_path)
        except (ImportError, ModuleNotFoundError, ValueError) as e:
            logger.debug("Filing class resolve: import_module %r failed: %s", module_path, e)
            continue
        try:
            cls = reduce(getattr, attr_path.split("."), module)
        except AttributeError as e:
            logger.debug("Filing class resolve: getattr %r on %r failed: %s", attr_path, module_path, e)
            continue
        if isinstance(cls, type) and issubclass(cls, Filing):
            resolved: type[Filing] = cast(type[Filing], cls)
            _REGISTRY[name] = resolved
            logger.debug("Filing class resolved by import: %s", name)
            return resolved
    return None


def resolve_filing_class(name: str | None) -> type[Filing] | None:
    """
    完全修飾クラス名から Filing サブクラスを解決する。
    レジストリに無い場合は完全修飾名による動的インポートを試みる。

    Args:
        name: 保存時に付与した _filing_class の値。None または未登録の場合は None を返す。

    Returns:
        登録またはインポートで解決できればそのクラス、そうでなければ None（呼び出し側で Filing に fallback する）
    """
    if not name:
        return None
    if name in _REGISTRY:
        return _REGISTRY[name]
    return _resolve_filing_class_by_import(name)
