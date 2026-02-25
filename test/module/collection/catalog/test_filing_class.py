"""
Catalog の _filing_class 振る舞いのテスト。

- index 時に data 辞書に _filing_class（完全修飾クラス名）が付与されること
- get_raw で取得した辞書に _filing_class が含まれること
- get で resolver が解決できる場合、正しい具象クラスで復元されること
- get で _filing_class が無い／解決できない場合は Filing にフォールバックすること
"""

import hashlib
import json
from datetime import datetime

from fino_filing import Catalog, EDINETFiling, Filing
from fino_filing.collection.filing_resolver import FilingResolver


def _index_filing(catalog: Catalog, filing: Filing) -> None:
    content = b"dummy"
    checksum = hashlib.sha256(content).hexdigest()
    if filing.checksum != checksum:
        return
    catalog.index(filing)


class TestCatalog_FilingClass_Behavior:
    """
    _filing_class の付与・取得・復元の振る舞いテスト
    """

    def test_get_raw_includes_filing_class_for_base_filing(
        self, temp_catalog: Catalog
    ) -> None:
        """Filing を index した場合、get_raw の辞書に _filing_class が含まれる（Filing の完全修飾名）"""
        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        filing = Filing(
            id="fc_base_001",
            source="test",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=datetime.now(),
        )
        temp_catalog.index(filing)

        raw = temp_catalog.get_raw("fc_base_001")
        assert raw is not None
        assert "_filing_class" in raw
        assert raw["_filing_class"] == "fino_filing.filing.filing.Filing"

    def test_get_raw_includes_filing_class_for_edinet_filing(
        self, temp_catalog: Catalog
    ) -> None:
        """EDINETFiling を index した場合、get_raw の辞書に _filing_class が EDINETFiling の完全修飾名で含まれる"""
        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        now = datetime.now()
        filing = EDINETFiling(
            id="fc_edinet_001",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=now,
            doc_id="doc1",
            edinet_code="E12345",
            sec_code="12345",
            jcn="1234567890123",
            filer_name="Test Inc.",
            ordinance_code="010",
            form_code="030101",
            doc_type_code="120",
            doc_description="有価証券報告書",
            period_start=now,
            period_end=now,
            submit_datetime=now,
        )
        temp_catalog.index(filing)

        raw = temp_catalog.get_raw("fc_edinet_001")
        assert raw is not None
        assert "_filing_class" in raw
        assert "EDINETFiling" in raw["_filing_class"]
        assert raw["_filing_class"] == "fino_filing.filing.filing_edinet.EDINETFiling"

    def test_get_returns_edinet_filing_when_resolver_knows_it(
        self, temp_catalog: Catalog
    ) -> None:
        """default_resolver が EDINETFiling を登録しているため、get で EDINETFiling として復元される"""
        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        now = datetime.now()
        filing = EDINETFiling(
            id="fc_get_edinet_001",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=now,
            doc_id="doc1",
            edinet_code="E12345",
            sec_code="12345",
            jcn="1234567890123",
            filer_name="Test Inc.",
            ordinance_code="010",
            form_code="030101",
            doc_type_code="120",
            doc_description="有価証券報告書",
            period_start=now,
            period_end=now,
            submit_datetime=now,
        )
        temp_catalog.index(filing)

        restored = temp_catalog.get("fc_get_edinet_001")
        assert restored is not None
        assert isinstance(restored, EDINETFiling)
        assert restored.doc_id == "doc1"
        assert restored.filer_name == "Test Inc."

    def test_get_returns_filing_when_indexed_as_base(
        self, temp_catalog: Catalog
    ) -> None:
        """Filing として index した場合は get で Filing として復元される"""
        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        filing = Filing(
            id="fc_get_base_001",
            source="test",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=datetime.now(),
        )
        temp_catalog.index(filing)

        restored = temp_catalog.get("fc_get_base_001")
        assert restored is not None
        assert type(restored).__name__ == "Filing"
        assert restored.id == "fc_get_base_001"

    def test_get_returns_filing_fallback_when_resolver_unknown(
        self, temp_catalog: Catalog
    ) -> None:
        """_filing_class が resolver で解決できない場合、Filing にフォールバックする"""

        class RegistryOnlyResolver(FilingResolver):
            """動的インポートを行わずレジストリのみ参照する resolver（未登録は None）"""

            def resolve(self, name):  # type: ignore[no-untyped-def]
                return self._registry.get(name) if name else None

        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        now = datetime.now()
        edinet_filing = EDINETFiling(
            id="fc_fallback_001",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=now,
            doc_id="d1",
            edinet_code="E1",
            sec_code="1",
            jcn="1",
            filer_name="F",
            ordinance_code="010",
            form_code="030101",
            doc_type_code="120",
            doc_description="d",
            period_start=now,
            period_end=now,
            submit_datetime=now,
        )
        temp_catalog.index(edinet_filing)
        catalog_path = temp_catalog.db_path
        temp_catalog.close()

        resolver = RegistryOnlyResolver()
        catalog = Catalog(catalog_path, resolver=resolver)
        raw = catalog.get_raw("fc_fallback_001")
        assert raw is not None
        assert "EDINETFiling" in raw["_filing_class"]

        restored = catalog.get("fc_fallback_001")
        assert restored is not None
        assert type(restored).__name__ == "Filing"
        catalog.close()

    def test_filing_class_stored_as_physical_column(
        self, temp_catalog: Catalog
    ) -> None:
        """_filing_class が物理カラムとしてテーブルに存在し、SELECT で取得できる"""
        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        filing = Filing(
            id="fc_phys_001",
            source="test",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=datetime.now(),
        )
        temp_catalog.index(filing)

        row = temp_catalog.conn.execute(
            'SELECT "_filing_class" FROM filings WHERE id = ?', ["fc_phys_001"]
        ).fetchone()
        assert row is not None
        assert row[0] == "fino_filing.filing.filing.Filing"

    def test_data_column_contains_only_extra_fields_not_core(
        self, temp_catalog: Catalog
    ) -> None:
        """data カラムには core / _filing_class を保存せず、追加フィールドのみ保存される"""
        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        filing = Filing(
            id="fc_data_only_001",
            source="test",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=datetime.now(),
        )
        temp_catalog.index(filing)

        row = temp_catalog.conn.execute(
            "SELECT data FROM filings WHERE id = ?", ["fc_data_only_001"]
        ).fetchone()
        assert row is not None
        data_parsed = json.loads(row[0])
        for key in (
            "id",
            "source",
            "checksum",
            "name",
            "is_zip",
            "format",
            "created_at",
            "_filing_class",
        ):
            assert key not in data_parsed, f"data に {key} が含まれてはいけない"
        assert data_parsed == {}

    def test_data_column_contains_only_extra_fields_edinet(
        self, temp_catalog: Catalog
    ) -> None:
        """EDINETFiling では data に追加フィールド（indexed でないもの）のみ入る想定；core と _filing_class は入らない"""
        content = b"dummy"
        checksum = hashlib.sha256(content).hexdigest()
        now = datetime.now()
        filing = EDINETFiling(
            id="fc_data_edinet_001",
            checksum=checksum,
            name="f.txt",
            is_zip=False,
            format="xbrl",
            created_at=now,
            doc_id="d1",
            edinet_code="E1",
            sec_code="1",
            jcn="1",
            filer_name="F",
            ordinance_code="010",
            form_code="030101",
            doc_type_code="120",
            doc_description="d",
            period_start=now,
            period_end=now,
            submit_datetime=now,
        )
        temp_catalog.index(filing)

        row = temp_catalog.conn.execute(
            "SELECT data FROM filings WHERE id = ?", ["fc_data_edinet_001"]
        ).fetchone()
        assert row is not None
        data_parsed = json.loads(row[0])
        for key in (
            "id",
            "source",
            "checksum",
            "name",
            "is_zip",
            "format",
            "created_at",
            "_filing_class",
        ):
            assert key not in data_parsed, f"data に {key} が含まれてはいけない"
        # EDINETFiling の追加フィールドは indexed なので物理カラムに入り、data には core 以外の非 indexed のみ
        # ここでは core/_filing_class が data に無いことだけ検証
        full = temp_catalog.get_raw("fc_data_edinet_001")
        assert full is not None
        assert full["id"] == "fc_data_edinet_001"
        assert full["_filing_class"] == "fino_filing.filing.filing_edinet.EDINETFiling"
