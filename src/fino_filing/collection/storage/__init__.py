# collection/storage/__init__.py
"""Storage抽象化（pathを意識しない設計）"""

from typing import Iterator, Protocol

from .flat_local import FlatLocalStorage


class Storage(Protocol):
    """Storage抽象化（filing_idで参照、物理配置に無関心）"""

    def save(self, filing_id: str, content: bytes, metadata: dict | None = None) -> str:
        """
        Filing保存

        Returns:
            実際に保存されたパス（Storage実装に依存）
        """
        ...

    def load(self, filing_id: str) -> bytes:
        """Filing読み込み（filing_idで直接アクセス）"""
        ...

    def exists(self, filing_id: str) -> bool:
        """存在確認"""
        ...

    def list_all(self) -> Iterator[str]:
        """全filing_id列挙"""
        ...

    def get_path(self, filing_id: str) -> str | None:
        """
        実際の物理パス取得（デバッグ用）
        Collectionは通常これを使わない
        """
        ...

    def get_metadata(self, filing_id: str) -> dict | None:
        """Registryに格納されたmetadata取得（rebuild用）"""
        ...


__all__ = [
    "Storage",
    "FlatLocalStorage",
]
