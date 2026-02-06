import hashlib
import logging
from pathlib import Path
from typing import Any, Optional

from fino_filing.collection.index_db import IndexDB
from fino_filing.collection.models import CoreFiling, filing_from_dict
from fino_filing.collection.storage import FlatLocalStorage

logger = logging.getLogger(__name__)


class Collection:
    """Collection Facade（Filing IDの一意性保証・検索インデックス提供）"""

    def __init__(
        self, storage: Optional[Any] = None, index_db: Optional[IndexDB] = None
    ) -> None:
        # Default configuration
        if storage is None or index_db is None:
            default_dir = Path.cwd() / ".fino" / "collection"
            default_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Using default collection directory: %s", default_dir)

            if storage is None:
                storage = FlatLocalStorage(default_dir)
                logger.info("Initialized default FlatLocalStorage")

            if index_db is None:
                index_db_path = default_dir / "index.db"
                index_db = IndexDB(str(index_db_path))
                logger.info("Initialized default IndexDB at %s", index_db_path)

        self.storage = storage
        self.index_db = index_db

    # ========== 追加系 ==========

    def add(self, filing: CoreFiling, content: bytes) -> str:
        """Filing追加"""
        # 1. Checksum検証
        actual_checksum = hashlib.sha256(content).hexdigest()
        if actual_checksum != filing.checksum:
            raise ValueError(
                f"Checksum mismatch: {actual_checksum} != {filing.checksum}"
            )

        # 2. 重複チェック
        if self.storage.exists(filing.filing_id):
            raise ValueError(f"Filing {filing.filing_id} already exists")

        # 3. Storage保存（metadataをRegistryに格納）
        metadata = filing.to_dict()
        actual_path = self.storage.save(filing.filing_id, content, metadata)

        # 4. Index DB登録
        self.index_db.index(filing)

        return actual_path

    # ========== 検索系 ==========

    def find(self, **filters) -> list[CoreFiling]:
        """検索"""
        results = self.index_db.search(**filters)
        return [filing_from_dict(dict(r), self.storage) for r in results]

    def get(self, filing_id: str) -> CoreFiling | None:
        """ID取得"""
        data = self.index_db.get(filing_id)
        if not data:
            return None
        return filing_from_dict(data, self.storage)

    def exists(self, filing_id: str) -> bool:
        """存在確認"""
        return self.storage.exists(filing_id)

    # ========== 管理系 ==========

    def rebuild_index(self) -> None:
        """Index DB再構築（Storageのlist_all + metadataから）"""
        logger.info("Rebuilding index from storage...")
        self.index_db.rebuild(self.storage)
        logger.info("Index rebuild complete")

    def verify_integrity(self) -> dict:
        """整合性検証"""
        issues = {
            "checksum_mismatch": [],
            "missing_in_storage": [],
            "missing_in_index": [],
        }

        # Index → Storage
        for filing_data in self.index_db.search():
            filing_id = filing_data["filing_id"]
            if not self.storage.exists(filing_id):
                issues["missing_in_storage"].append(filing_id)
                continue

            # Checksum検証
            try:
                filing = filing_from_dict(dict(filing_data), self.storage)
                if not filing.verify_checksum():
                    issues["checksum_mismatch"].append(filing_id)
            except Exception as e:
                logger.warning("Checksum verification failed for %s: %s", filing_id, e)

        # Storage → Index
        for filing_id in self.storage.list_all():
            if not self.index_db.get(filing_id):
                issues["missing_in_index"].append(filing_id)

        return issues

    def migrate(self, new_storage: Any) -> None:
        """Storage移行"""
        logger.info("Migrating storage...")

        count = 0
        for filing_id in self.storage.list_all():
            content = self.storage.load(filing_id)
            metadata = getattr(self.storage, "get_metadata", lambda _: None)(filing_id)
            new_storage.save(filing_id, content, metadata)
            count += 1

        logger.info("Migrated %d filings", count)
        self.storage = new_storage
