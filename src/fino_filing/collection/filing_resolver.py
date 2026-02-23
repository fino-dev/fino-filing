"""
Filing 具象クラス解決器

責務:
- 完全修飾クラス名と Filing サブクラスのマッピングを保持する
- Catalog の get/search で _filing_class から復元に使うクラスを解決する
- 未登録の場合は完全修飾名から動的インポートで解決を試みる
"""

from __future__ import annotations

import importlib
import logging
from functools import reduce
from typing import Optional, cast

from fino_filing.filing.filing import Filing

logger = logging.getLogger(__name__)


class FilingResolver:
    """
    Filing 具象クラス解決器（Catalog が所有する）

    Catalog が index 時に付与した _filing_class（完全修飾クラス名）から、
    復元に使う Filing サブクラスを解決する責務を担う。
    """

    def __init__(self) -> None:
        self._registry: dict[str, type[Filing]] = {}

    def register(self, cls: type[Filing]) -> None:
        """Filing サブクラスを完全修飾クラス名で登録する。"""
        name = f"{cls.__module__}.{cls.__qualname__}"
        self._registry[name] = cls

    def resolve(self, name: Optional[str]) -> Optional[type[Filing]]:
        """
        完全修飾クラス名から Filing サブクラスを解決する。

        1. 内部レジストリを参照する
        2. 未登録なら動的インポートを試みる
        3. 解決できなければ None を返す（呼び出し側で Filing にフォールバック）
        """
        if not name:
            return None
        if name in self._registry:
            return self._registry[name]
        return self._resolve_by_import(name)

    def _resolve_by_import(self, name: str) -> Optional[type[Filing]]:
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
                logger.debug(
                    "Filing class resolve: import_module %r failed: %s", module_path, e
                )
                continue
            try:
                cls = reduce(getattr, attr_path.split("."), module)
            except AttributeError as e:
                logger.debug(
                    "Filing class resolve: getattr %r on %r failed: %s",
                    attr_path,
                    module_path,
                    e,
                )
                continue
            if isinstance(cls, type) and issubclass(cls, Filing):
                resolved = cast(type[Filing], cls)
                self._registry[name] = resolved
                logger.debug("Filing class resolved by import: %s", name)
                return resolved
        return None


# パッケージ共通のデフォルトリゾルバー
# 組み込み Filing サブクラスは __init__.py で登録される
default_resolver = FilingResolver()


def register_filing_class(name: str, cls: type[Filing]) -> None:
    """
    完全修飾クラス名で Filing サブクラスを default_resolver に登録する。

    後方互換のために残している。通常は default_resolver.register() を使うこと。
    """
    default_resolver._registry[name] = cls
