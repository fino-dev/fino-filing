import hashlib
from datetime import datetime
from pathlib import Path

import pytest

from fino_filing import Catalog, Collection, EDINETFiling
from fino_filing.collection.storages import LocalStorage


@pytest.mark.module
@pytest.mark.collection
class TestCollection_Clear:
    """TestCollection.clear() Test"""

    def test_removes_catalog_rows_and_storage_files(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """カタログの全行と Locator が指すストレージ上のファイルが削除される"""
        content = b"payload"
        checksum = hashlib.sha256(content).hexdigest()
        f1 = EDINETFiling(
            id="clear_a",
            checksum=checksum,
            name="a.pdf",
            is_zip=False,
            format="pdf",
            created_at=datetime_now,
            doc_id="D1",
            edinet_code="E1",
            sec_code="11111",
            jcn="1111111111111",
            filer_name="A",
            ordinance_code="010",
            form_code="030000",
            doc_type_code="120",
            doc_description="A",
            period_start=datetime_now,
            period_end=datetime_now,
            submit_datetime=datetime_now,
        )
        f2 = EDINETFiling(
            id="clear_b",
            checksum=checksum,
            name="b.pdf",
            is_zip=False,
            format="pdf",
            created_at=datetime_now,
            doc_id="D2",
            edinet_code="E2",
            sec_code="22222",
            jcn="2222222222222",
            filer_name="B",
            ordinance_code="010",
            form_code="030000",
            doc_type_code="120",
            doc_description="B",
            period_start=datetime_now,
            period_end=datetime_now,
            submit_datetime=datetime_now,
        )
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        _, path_a = collection.add(f1, content)
        _, path_b = collection.add(f2, content)
        assert Path(path_a).is_file()
        assert Path(path_b).is_file()
        assert temp_catalog.get("clear_a") is not None
        assert temp_catalog.get("clear_b") is not None

        collection.clear()

        assert temp_catalog.get("clear_a") is None
        assert temp_catalog.get("clear_b") is None
        assert not Path(path_a).is_file()
        assert not Path(path_b).is_file()
        assert temp_catalog.stats()["total"] == 0

    def test_clear_on_empty_collection_is_noop(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
    ) -> None:
        """未追加の Collection で clear しても例外にならない"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        collection.clear()
        assert temp_catalog.stats()["total"] == 0
