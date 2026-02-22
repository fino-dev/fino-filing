from pathlib import Path
from typing import Iterator, Protocol


def _sanitize_storage_key(storage_key: str, base_dir: Path) -> Path:
    """
    storage_key を base_dir 内の有効な相対パスに正規化する。
    パストラバーサル（..）や base_dir 外への書き込みを防ぐ。
    """
    if not storage_key or storage_key.startswith("/"):
        raise ValueError("storage_key must be a non-empty relative path")
    path = Path(storage_key)
    if path.is_absolute():
        raise ValueError("storage_key must not be absolute")
    if ".." in path.parts:
        raise ValueError("storage_key must not contain '..'")
    resolved = (base_dir / path).resolve()
    base_resolved = base_dir.resolve()
    if not resolved.is_relative_to(base_resolved):
        raise ValueError("storage_key must not escape base_dir")
    return resolved


class Storage(Protocol):
    """Storage (Filing Storage <Adapter>)"""

    base_dir: Path

    def save(
        self,
        id_: str,
        content: bytes,
        metadata: dict | None = None,
        storage_key: str | None = None,
    ) -> str:
        """
        Filing保存。
        storage_key が渡された場合はそれを物理キー（Localでは相対パス）として使用する。

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
