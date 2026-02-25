"""Catalog の単体テスト。観点: 正常系（index_batch, search, count, clear）"""

from datetime import datetime

from fino_filing import Catalog, Expr, Filing


class TestCatalog_IndexBatch:
    """Catalog.index_batch. 観点: 正常系"""

    def test_index_batch_then_count(
        self,
        temp_catalog: Catalog,
    ) -> None:
        """index_batch で複数 Filing を登録し、count で件数が一致する"""
        now = datetime.now()
        filings = [
            Filing(
                id=f"id_{i}",
                source="src",
                checksum="c" * 64,
                name="n.xbrl",
                is_zip=False,
                format="xbrl",
                created_at=now,
            )
            for i in range(3)
        ]
        temp_catalog.index_batch(filings)
        assert temp_catalog.count() == 3


class TestCatalog_Search:
    """Catalog.search. 観点: 正常系"""

    def test_search_limit_offset(
        self,
        temp_catalog: Catalog,
    ) -> None:
        """search の limit / offset が効く"""
        now = datetime.now()
        for i in range(5):
            temp_catalog.index(
                Filing(
                    id=f"id_{i}",
                    source="src",
                    checksum="c" * 64,
                    name="n.xbrl",
                    is_zip=False,
                    format="xbrl",
                    created_at=now,
                )
            )
        all_results = temp_catalog.search(limit=10, offset=0)
        assert len(all_results) == 5
        limited = temp_catalog.search(limit=2, offset=0)
        assert len(limited) == 2
        offset_results = temp_catalog.search(limit=2, offset=2)
        assert len(offset_results) == 2


class TestCatalog_Count:
    """Catalog.count. 観点: 正常系"""

    def test_count_without_expr(
        self,
        temp_catalog: Catalog,
    ) -> None:
        """expr なしで count すると全件数"""
        now = datetime.now()
        temp_catalog.index(
            Filing(
                id="only",
                source="s",
                checksum="c" * 64,
                name="n.xbrl",
                is_zip=False,
                format="xbrl",
                created_at=now,
            )
        )
        assert temp_catalog.count() == 1

    def test_count_with_expr(
        self,
        temp_catalog: Catalog,
    ) -> None:
        """expr を渡すと条件に一致する件数"""
        now = datetime.now()
        temp_catalog.index(
            Filing(
                id="a1",
                source="s1",
                checksum="c" * 64,
                name="n.xbrl",
                is_zip=False,
                format="xbrl",
                created_at=now,
            )
        )
        temp_catalog.index(
            Filing(
                id="a2",
                source="s2",
                checksum="c" * 64,
                name="n.xbrl",
                is_zip=False,
                format="xbrl",
                created_at=now,
            )
        )
        expr = Expr("source = ?", ["s1"])
        assert temp_catalog.count(expr=expr) == 1


class TestCatalog_Clear:
    """Catalog.clear. 観点: 正常系"""

    def test_clear_removes_all(
        self,
        temp_catalog: Catalog,
    ) -> None:
        """clear 後に count が 0 になる"""
        now = datetime.now()
        temp_catalog.index(
            Filing(
                id="x",
                source="s",
                checksum="c" * 64,
                name="n.xbrl",
                is_zip=False,
                format="xbrl",
                created_at=now,
            )
        )
        assert temp_catalog.count() == 1
        temp_catalog.clear()
        assert temp_catalog.count() == 0
