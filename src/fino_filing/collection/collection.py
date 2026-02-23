import hashlib
import logging
from pathlib import Path
from typing import Optional

from fino_filing.collection.error import (
    CollectionChecksumMismatchError,
    LocatorPathResolutionError,
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
        self._locator = locator if locator is not None else Locator()

    # ========== 追加系 ==========

    def add(self, filing: Filing, content: bytes) -> tuple[Filing, str]:
        """
        Add Filing to the collection

        Args:
            filing: Filing to add
            content: Content to add

        Returns:
            tuple[Filing, str]: Filing and path
        """
        # Checksumチェック
        actual_checksum = hashlib.sha256(content).hexdigest()
        expected_checksum = filing.checksum
        if actual_checksum != expected_checksum:
            raise CollectionChecksumMismatchError(
                filing_id=filing.id,
                actual_checksum=actual_checksum,
                expected_checksum=expected_checksum,
            )

        filing_id = filing.id
        # pathを生成する (Locator)
        storage_key = self._locator.resolve(filing)
        if storage_key is None:
            raise LocatorPathResolutionError(filing=filing)

        # Catalog重複チェック or Catalog保存
        if self._catalog.get(filing_id) is not None:
            logger.warning(
                "Filing id: %s already exists in catalog so skip saving in catalog",
                filing_id,
            )
        else:
            self._catalog.index(filing)

        # Storage保存
        actual_path = self._storage.save(content, storage_key=storage_key)

        return filing, actual_path

    # ========== 検索系 ==========

    def get(self, id: str) -> tuple[Filing | None, bytes | None, str | None]:
        """ID specified retrieval (Filing and content)"""
        filing = self.get_filing(id)
        content = self.get_content(id)
        # pathをlocatorで取得 (get_pathは内部でget_filingを呼び出しているため、重複実行を避けるためここでは使用しない)
        path = self._locator.resolve(filing)
        return filing, content, path

    def get_filing(self, id: str) -> Filing | None:
        """ID specified retrieval (Filing only)"""
        return self._catalog.get(id)

    def get_content(self, id: str) -> bytes | None:
        """ID specified retrieval (Content only). PathはCatalog+Locatorで解決する。"""
        filing = self._catalog.get(id)
        if filing is None:
            return None
        path = self._locator.resolve(filing)
        if path is None:
            return None
        try:
            return self._storage.load_by_path(path)
        except FileNotFoundError:
            return None

    def get_path(self, id: str) -> str | None:
        """ID specified retrieval (Path only)"""
        filing = self.get_filing(id)
        return self._locator.resolve(filing)

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
