from fino_filing.collection.registry import RegistryManager

from fino_filing.collection.index_db import IndexDB
from fino_filing.collection.models import Filing
from fino_filing.collection.spec import CollectionSpec


class Collection:
    """Collection Facade（統一API）"""

    def __init__(
        self,
        storage,
        index_db: IndexDB,
        registry_mgr: RegistryManager,
        spec: CollectionSpec,
    ):
        self.storage = storage
        self.index_db = index_db
        self.registry_mgr = registry_mgr
        self.spec = spec

    # ========== 追加系 ==========

    def add(self, filing: Filing, content: bytes) -> str:
        """Filing追加（DB + Registry 両方に登録）"""
        # 1. Checksum検証
        import hashlib

        actual_checksum = hashlib.sha256(content).hexdigest()
        if actual_checksum != filing.checksum:
            raise ValueError(
                f"Checksum mismatch: {actual_checksum} != {filing.checksum}"
            )

        # 2. Payload保存
        path = self._compute_path(filing)
        self.storage.save(path, content)

        # 3. Index DB登録
        filing_with_path = Filing(
            **{**filing.to_dict(), "_path": path},
            _storage=self.storage,
        )
        self.index_db.index(filing_with_path)

        # 4. Registry登録
        directory = path.rsplit("/", 1)[0]
        self.registry_mgr.register(filing_with_path, directory)

        return path

    def _compute_path(self, filing: Filing) -> str:
        """パス計算（Partition戦略使用）"""
        # 簡易実装（本来は別のPartition strategyが必要）
        submit_date = filing.submit_date
        return f"{filing.source}/{submit_date.year}/{submit_date.month:02d}/{filing.filing_id}.zip"

    # ========== 検索系 ==========

    def find(self, **filters) -> list[Filing]:
        """検索（Index DB使用）"""
        results = self.index_db.search(**filters)
        return [Filing.from_dict(r, self.storage) for r in results]

    def get(self, filing_id: str) -> Filing | None:
        """ID取得"""
        data = self.index_db.get(filing_id)
        if not data:
            return None
        return Filing.from_dict(data, self.storage)

    # ========== 管理系 ==========

    def rebuild_index(self):
        """Index DB再構築（Registry から）"""
        print("Rebuilding index from registries...")
        self.index_db.rebuild(self.registry_mgr)
        print("Index rebuild complete")

    def verify_integrity(self) -> dict:
        """整合性検証"""
        issues = {
            "checksum_mismatch": [],
            "missing_payload": [],
            "orphaned_index": [],
        }

        # Index DBの全Filingを検証
        for filing_data in self.index_db.search():
            filing = Filing.from_dict(filing_data, self.storage)

            # Payload存在確認
            path = filing.metadata.get("_path")
            if not path or not self.storage.exists(path):
                issues["missing_payload"].append(filing.filing_id)
                continue

            # Checksum検証
            try:
                if not filing.verify_checksum():
                    issues["checksum_mismatch"].append(filing.filing_id)
            except Exception as e:
                print(f"Checksum verification failed for {filing.filing_id}: {e}")

        return issues

    def migrate(self, new_storage):
        """Storage移行（Local → S3等）"""
        print("Migrating storage...")

        count = 0
        for filing_data in self.index_db.search():
            filing = Filing.from_dict(filing_data, self.storage)

            # 旧Storageから読み込み
            content = filing.get_content()

            # 新Storageに保存
            path = filing.metadata["_path"]
            new_storage.save(path, content)

            count += 1

        print(f"Migrated {count} filings")

        # Storage切り替え
        self.storage = new_storage
