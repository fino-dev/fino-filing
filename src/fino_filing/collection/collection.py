import hashlib
import logging
from pathlib import Path
from typing import Optional

from fino_filing.collection.error import CollectionChecksumMismatchError
from fino_filing.filing.expr import Expr
from fino_filing.filing.filing import Filing

from .catalog import Catalog
from .locator import Locator
from .storage import Storage
from .storage.flat_local import LocalStorage

logger = logging.getLogger(__name__)


class Collection:
    """
    Collection (Filing Collection <Facade>)

    Methods:
    - add: Add Filing to the collection
    - get: Get Filing from the collection by ID
    - find: Search Filing from the collection
    - clear: Clear the collection
    - close: Close the collection
    """

    def __init__(
        self,
        storage: Optional[Storage] = None,
        catalog: Optional[Catalog] = None,
        locator: Optional[Locator] = None,
    ) -> None:
        # Default configuration
        if storage is None or catalog is None:
            # デフォルトのディレクトリはCurrent Working Directoryの.fino/collectionにする
            default_dir = Path.cwd() / ".fino" / "collection"
            default_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Using default collection directory: %s", default_dir)

            if storage is None:
                storage = LocalStorage(default_dir)
                logger.info("Initialized default LocalStorage")

            if catalog is None:
                catalog_path = default_dir / "index.db"
                catalog = Catalog(str(catalog_path))
                logger.info("Initialized default Catalog at %s", catalog_path)

        self._storage = storage
        self._catalog = catalog

    # ========== 追加系 ==========

    def add(self, filing: Filing, content: bytes) -> tuple[Filing, str]:
        """Filing追加"""
        # 1. Checksum検証
        actual_checksum = hashlib.sha256(content).hexdigest()
        expected_checksum = filing.checksum
        if actual_checksum != expected_checksum:
            raise CollectionChecksumMismatchError(
                filing_id=filing.id,
                actual_checksum=actual_checksum,
                expected_checksum=expected_checksum,
            )

        # 2. 重複チェック
        id_ = filing.id
        if id_ is None:
            raise ValueError("id is required")
        if self._storage.exists(id_):
            raise ValueError(f"Filing {id_} already exists")

        # 3. Storage保存（metadataをRegistryに格納）
        metadata = filing.to_dict()
        actual_path = self._storage.save(id_, content, metadata)

        # 4. pathを設定してCatalog登録
        self._catalog.index(filing)

        return filing, actual_path

    # ========== 検索系 ==========

    def get(self, id_: str) -> Filing | None:
        """ID取得"""
        data = self._catalog.get(id_)
        if not data:
            return None
        return Filing.from_dict(data, self._storage)

    def find(
        self,
        expr: "Expr | None" = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        desc: bool = True,
    ) -> list[Filing]:
        """検索"""
        results = self._catalog.search(
            expr=expr,
            limit=limit,
            offset=offset,
            order_by=order_by,
            desc=desc,
        )
        return [Filing.from_dict(dict(r), self._storage) for r in results]
