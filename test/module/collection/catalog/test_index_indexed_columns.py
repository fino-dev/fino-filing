"""
Catalog の indexed フィールド動的物理カラム化のテスト。

- index で indexed を持つ継承 Filing を登録するとテーブルにカラムが追加されること
- get で復元した Filing に拡張 indexed フィールドの値が含まれること
- search の order_by に拡張 indexed カラムを指定できること
- index_batch で複数種類の Filing を混在させても正しく保存・復元できること
"""

import hashlib
from datetime import datetime
from typing import Annotated

from fino_filing import Catalog, Field, Filing


def _table_columns(catalog: Catalog) -> set[str]:
    """filings テーブルのカラム名一覧を取得（テスト用）。"""
    rows = catalog.conn.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'filings'
        ORDER BY ordinal_position
        """
    ).fetchall()
    return {row[0] for row in rows}


class TestCatalog_Index_IndexedColumns:
    """
    Catalog.index() で indexed フィールドが物理カラムとして追加されることのテスト
    """

    def test_index_adds_physical_columns_for_extended_indexed_fields(
        self, temp_catalog: Catalog
    ) -> None:
        """indexed=True のフィールドを持つ継承 Filing を index すると、そのカラムがテーブルに追加される"""
        catalog = temp_catalog
        initial_columns = _table_columns(catalog)
        assert "ticker" not in initial_columns

        class ExtendedFiling(Filing):
            ticker: Annotated[str, Field(indexed=True, description="Ticker")]

        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        filing = ExtendedFiling(
            id="ext_001",
            source="test",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=datetime.now(),
            ticker="7203",
        )
        catalog.index(filing)

        columns = _table_columns(catalog)
        assert "ticker" in columns
        assert initial_columns < columns

    def test_get_raw_includes_extended_indexed_field_in_data(
        self, temp_catalog: Catalog
    ) -> None:
        """index した拡張 Filing の get_raw で、拡張 indexed フィールドが data 辞書に含まれる"""
        catalog = temp_catalog

        class ExtendedFiling(Filing):
            ticker: Annotated[str, Field(indexed=True, description="Ticker")]

        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        created = datetime(2024, 1, 15, 10, 0, 0)
        filing = ExtendedFiling(
            id="get_ext_001",
            source="test",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=created,
            ticker="7203",
        )
        catalog.index(filing)

        restored = catalog.get("get_ext_001")
        assert restored is not None
        assert restored.id == "get_ext_001"

        raw = catalog.get_raw("get_ext_001")
        assert raw is not None
        assert raw.get("ticker") == "7203"

    def test_search_order_by_extended_indexed_column(
        self, temp_catalog: Catalog
    ) -> None:
        """拡張 indexed カラムで order_by して search できる"""
        catalog = temp_catalog

        class ExtendedFiling(Filing):
            ticker: Annotated[str, Field(indexed=True, description="Ticker")]

        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        base_time = datetime(2024, 1, 15, 10, 0, 0)

        for i, ticker in enumerate(["0001", "0002", "0003"]):
            filing = ExtendedFiling(
                id=f"search_order_{i}",
                source="test",
                checksum=checksum,
                name="f.txt",
                is_zip=False,
                format="xbrl",
                created_at=base_time,
                ticker=ticker,
            )
            catalog.index(filing)

        results = catalog.search(order_by="ticker", limit=10, desc=False)
        assert len(results) >= 3
        tickers = [
            catalog.get_raw(r.id).get("ticker")
            for r in results
            if catalog.get_raw(r.id) and catalog.get_raw(r.id).get("ticker") is not None
        ]
        assert len(tickers) >= 3
        assert tickers == sorted(tickers)

    def test_index_batch_mixed_filing_types(
        self, temp_catalog: Catalog
    ) -> None:
        """index_batch で基本 Filing と拡張 Filing を混在させても正しく保存・復元される"""
        catalog = temp_catalog

        class ExtendedFiling(Filing):
            ticker: Annotated[str, Field(indexed=True, description="Ticker")]

        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        now = datetime.now()

        base_filing = Filing(
            id="batch_base_001",
            source="test",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=now,
        )
        extended_filing = ExtendedFiling(
            id="batch_ext_001",
            source="test",
            checksum=checksum,
            name="f2.txt",
            is_zip=False,
            format="xbrl",
            created_at=now,
            ticker="7203",
        )

        catalog.index_batch([base_filing, extended_filing])

        base_restored = catalog.get("batch_base_001")
        ext_restored = catalog.get("batch_ext_001")

        assert base_restored is not None
        assert base_restored.id == "batch_base_001"
        assert ext_restored is not None
        assert ext_restored.id == "batch_ext_001"

        raw_ext = catalog.get_raw("batch_ext_001")
        assert raw_ext is not None
        assert raw_ext.get("ticker") == "7203"
