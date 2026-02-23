from pathlib import Path
from typing import Protocol


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
        content: bytes,
        storage_key: str | None = None,
    ) -> str:
        """
        Save content to the storage
        - save content to the storage_key path (relative path)

        Args:
            content: Content to save
            storage_key: Storage key (relative path)

        Returns:
            str: Saved absolute path
        """
        ...

    def load_by_path(self, relative_path: str) -> bytes:
        """相対パス指定でFiling実体を読み込む。id→pathの解決は呼び出し側（Catalog+Locator）の責務。"""
        ...
