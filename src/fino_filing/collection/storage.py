from pathlib import Path
from typing import Iterator, Protocol


class Storage(Protocol):
    """Storage (Filing Storage <Adapter>)"""

    base_dir: Path

    def save(self, id_: str, content: bytes, metadata: dict | None = None) -> str:
        """
        Filing保存

        Returns:
            実際に保存されたパス（Storage実装に依存）
        """
        ...

    def load(self, id_: str) -> bytes:
        """Filing読み込み（idで直接アクセス）"""
        ...

    def exists(self, id_: str) -> bool:
        """存在確認"""
        ...

    def list_all(self) -> Iterator[str]:
        """全id列挙"""
        ...

    def get_path(self, id_: str) -> str | None:
        """
        実際の物理パス取得（デバッグ用）
        Collectionは通常これを使わない
        """
        ...

    def get_metadata(self, id_: str) -> dict | None:
        """Registryに格納されたmetadata取得"""
        ...
