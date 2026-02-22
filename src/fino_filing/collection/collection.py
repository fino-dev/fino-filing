import hashlib
import logging
from pathlib import Path
from typing import Optional

from fino_filing.collection.error import (
    CatalogAlreadyExistsError,
    CatalogRequiredValueError,
    CollectionChecksumMismatchError,
)
from fino_filing.filing.expr import Expr
from fino_filing.filing.filing import Filing

from .catalog import Catalog
from .locator import Locator
from .storage import Storage
from .storages import LocalStorage

logger = logging.getLogger(__name__)


class Collection:
    """
    Collection (Filing Collection <Facade>)

    Methods:
    - add: Add Filing to the collection
    - get: Get Filing from the collection by ID
    - get_filing: Get Filing from the collection by ID
    - get_content: Get saved file bytes by ID (e.g. for arelle parsing)
    - search: Search Filing from the collection
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
        """Add Filing to the collection"""
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
            raise CatalogRequiredValueError(field="id", actual_value=id_)
        if self._storage.exists(id_):
            raise CatalogAlreadyExistsError(filing_id=id_)

        # 3. Storage保存（metadataをRegistryに格納）
        metadata = filing.to_dict()
        actual_path = self._storage.save(id_, content, metadata)

        # 4. pathを設定してCatalog登録
        self._catalog.index(filing)

        return filing, actual_path

    # ========== 検索系 ==========

    def get(self, id: str) -> tuple[Filing | None, bytes | None]:
        """ID specified retrieval (Filing and content)"""
        filing = self.get_filing(id)
        content = self.get_content(id)
        return filing, content

    def get_filing(self, id: str) -> Filing | None:
        """ID specified retrieval (Filing only)"""
        return self._catalog.get(id)

    def get_content(self, id: str) -> bytes | None:
        """ID specified retrieval (Content only)"""
        try:
            return self._storage.load(id)
        except FileNotFoundError:
            return None

    def search(
        self,
        expr: "Expr | None" = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        desc: bool = True,
    ) -> list[Filing]:
        """Search (Expression API)"""
        return self._catalog.search(
            expr=expr,
            limit=limit,
            offset=offset,
            order_by=order_by,
            desc=desc,
        )
