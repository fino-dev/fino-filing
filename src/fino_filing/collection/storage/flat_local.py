# collection/storage/flat_local.py
"""完全フラット構造のLocalStorage実装"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)


class FlatLocalStorage:
    """完全フラット構造（単一ディレクトリ・単一Registry）"""

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

    def save(self, filing_id: str, content: bytes, metadata: dict | None = None) -> str:
        """保存（ファイル名=checksum）"""
        checksum = hashlib.sha256(content).hexdigest()
        filename = f"{checksum}.zip"

        file_path = self.base_dir / filename
        file_path.write_bytes(content)

        self._index[filing_id] = filename
        if metadata is not None:
            self._metadata[filing_id] = metadata
        self._save_registry()

        return str(file_path)

    def load(self, filing_id: str) -> bytes:
        """読み込み"""
        filename = self._index.get(filing_id)
        if not filename:
            raise FileNotFoundError(f"Filing {filing_id} not found in registry")

        file_path = self.base_dir / filename
        return file_path.read_bytes()

    def exists(self, filing_id: str) -> bool:
        """存在確認"""
        return filing_id in self._index

    def list_all(self) -> Iterator[str]:
        """全filing_id列挙"""
        return iter(self._index.keys())

    def get_path(self, filing_id: str) -> str | None:
        """物理パス取得"""
        filename = self._index.get(filing_id)
        return str(self.base_dir / filename) if filename else None

    def get_metadata(self, filing_id: str) -> dict | None:
        """Registryに格納されたmetadata取得"""
        return self._metadata.get(filing_id)
