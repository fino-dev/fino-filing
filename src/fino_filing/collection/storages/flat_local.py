# collection/storage/flat_local.py
"""完全フラット構造のLocalStorage実装（path解決はLocatorに委譲）"""

import logging
from pathlib import Path
from typing import Any

from fino_filing.collection.storage import _sanitize_storage_key

logger = logging.getLogger(__name__)


class LocalStorage:
    """完全フラット構造 ローカルFS実装。id→pathの解決は行わず、呼び出し側が渡すstorage_key（相対パス）で読み書きする。"""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        id_: str,
        content: bytes,
        metadata: dict[str, Any] | None = None,
        storage_key: str | None = None,
    ) -> str:
        """
        保存。
        storage_key（Locatorで解決された相対パス）を必須とし、そのパスに書き込む。
        """
        if storage_key is None:
            raise ValueError("storage_key is required (resolve path via Locator)")
        full_path = _sanitize_storage_key(storage_key, self.base_dir)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        return str(full_path)

    def load_by_path(self, relative_path: str) -> bytes:
        """相対パス指定で読み込み。"""
        full_path = _sanitize_storage_key(relative_path, self.base_dir)
        return full_path.read_bytes()
