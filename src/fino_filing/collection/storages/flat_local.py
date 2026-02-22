# collection/storage/flat_local.py
"""完全フラット構造のLocalStorage実装"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Iterator

from fino_filing.collection.storage import _sanitize_storage_key

logger = logging.getLogger(__name__)


class LocalStorage:
    """完全フラット構造 ローカルFS実装（単一ディレクトリ・単一Registry）"""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.base_dir / ".fino_registry.json"
        self._index: dict[str, str] = {}
        self._metadata: dict[str, dict] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        """Registry読み込み"""
        if not self.registry_path.exists():
            return

        with open(self.registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._index = data.get("index", {})
            self._metadata = data.get("metadata", {})

    def _save_registry(self) -> None:
        """Registry保存"""
        data = {
            "version": "1.0",
            "storage_type": "flat",
            "index": self._index,
            "metadata": self._metadata,
        }
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save(
        self,
        id_: str,
        content: bytes,
        metadata: dict[str, Any] | None = None,
        storage_key: str | None = None,
    ) -> str:
        """
        保存。
        storage_key が渡された場合はそれを相対パスとして使用し、
        渡されない場合は従来どおり {checksum}.zip で保存する（後方互換）。
        """
        if storage_key is not None:
            full_path = _sanitize_storage_key(storage_key, self.base_dir)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_bytes(content)
            registry_key = str(full_path.relative_to(self.base_dir.resolve()))
        else:
            checksum = hashlib.sha256(content).hexdigest()
            filename = f"{checksum}.zip"
            full_path = self.base_dir / filename
            full_path.write_bytes(content)
            registry_key = filename

        self._index[id_] = registry_key
        if metadata is not None:
            self._metadata[id_] = metadata
        self._save_registry()

        return str(full_path)

    def load(self, id_: str) -> bytes:
        """読み込み"""
        filename = self._index.get(id_)
        if not filename:
            raise FileNotFoundError(f"Filing {id_} not found in registry")

        file_path = self.base_dir / filename
        return file_path.read_bytes()

    def exists(self, id_: str) -> bool:
        """存在確認"""
        return id_ in self._index

    def list_all(self) -> Iterator[str]:
        """全id列挙"""
        return iter(self._index.keys())

    def get_path(self, id_: str) -> str | None:
        """物理パス取得"""
        filename = self._index.get(id_)
        return str(self.base_dir / filename) if filename else None

    def get_metadata(self, id_: str) -> dict | None:
        """Registryに格納されたmetadata取得"""
        return self._metadata.get(id_)
