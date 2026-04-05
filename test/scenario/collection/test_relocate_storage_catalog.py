"""Scenario: copy storage tree and catalog DB to new paths and reopen Collection."""

from __future__ import annotations

import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from fino_filing import Catalog, Collection, Filing, LocalStorage
from fino_filing.util.content import sha256_checksum


@pytest.mark.scenario
@pytest.mark.collection
class TestScenario_RelocateStorageCatalog:
    """Scenario: Relocate storage and catalog Test"""

    def test_copy_storage_and_index_then_collection_roundtrip(self) -> None:
        """ストレージディレクトリと index.db を別パスに複製し、新しい Collection で読み取れる"""
        with tempfile.TemporaryDirectory(prefix="scenario_reloc_src_") as src_root:
            src_base = Path(src_root)
            storage_path_a = src_base / "data_a"
            db_path_a = src_base / "index_a.db"

            catalog_a = Catalog(str(db_path_a))
            storage_a = LocalStorage(storage_path_a)
            collection_a = Collection(storage=storage_a, catalog=catalog_a)

            content = b"relocate-me"
            checksum = sha256_checksum(content)
            filing = Filing(
                id="reloc-1",
                source="LOCAL",
                checksum=checksum,
                name="holdings.csv",
                is_zip=False,
                format="csv",
                created_at=datetime(2024, 5, 5, 10, 0, 0),
            )
            collection_a.add(filing, content)

            catalog_a.close()

            dest_base = src_base / "migrated"
            dest_base.mkdir()
            shutil.copytree(storage_path_a, dest_base / "data_b")
            shutil.copy2(db_path_a, dest_base / "index_b.db")

            catalog_b = Catalog(str(dest_base / "index_b.db"))
            storage_b = LocalStorage(dest_base / "data_b")
            collection_b = Collection(storage=storage_b, catalog=catalog_b)

            try:
                loaded = collection_b.get_filing("reloc-1")
                assert loaded is not None
                assert loaded.name == "holdings.csv"
                raw = collection_b.get_content("reloc-1")
                assert raw == content
                f2, c2, p2 = collection_b.get("reloc-1")
                assert f2 is not None and c2 == content and p2 is not None
            finally:
                catalog_b.close()
