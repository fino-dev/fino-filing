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
from typing import Any

from fino_filing import Catalog, EDINETFiling, Expr, Field, Filing
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


class TestCatalog_Helper_expr_to_inline_sql:
    """
    Catalog._expr_to_inline_sql のテスト
    - Expr のプレースホルダをエスケープしたリテラルで置換した SQL を返す
    - indexed_columns を渡すと json_extract(data, '$.col') を "col" に書き換える
    """

    def test_replaces_single_placeholder_with_escaped_literal(
        self, temp_catalog: Catalog
    ) -> None:
        """プレースホルダ1つがエスケープされたリテラルで置換される（str, int, None, bool）"""
        assert Catalog._expr_to_inline_sql(Expr("x = ?", ["a"])) == "x = 'a'"
        assert Catalog._expr_to_inline_sql(Expr("x = ?", [100])) == "x = 100"
        assert Catalog._expr_to_inline_sql(Expr("x = ?", [None])) == "x = NULL"
        assert Catalog._expr_to_inline_sql(Expr("x = ?", [True])) == "x = TRUE"
        assert Catalog._expr_to_inline_sql(Expr("x = ?", [False])) == "x = FALSE"

    def test_replaces_placeholder_with_escaped_string_containing_quote(
        self, temp_catalog: Catalog
    ) -> None:
        """str にシングルクォートが含まれる場合は '' にエスケープされる"""
        assert Catalog._expr_to_inline_sql(Expr("x = ?", ["O'Brien"])) == (
            "x = 'O''Brien'"
        )

    def test_replaces_placeholder_with_datetime_literal(
        self, temp_catalog: Catalog, datetime_now: datetime
    ) -> None:
        """datetime は ISO 形式のクォート付きリテラルに置換される"""
        expected = f"x = '{datetime_now.isoformat()}'"
        assert Catalog._expr_to_inline_sql(Expr("x = ?", [datetime_now])) == expected

    def test_replaces_json_extract_with_physical_column_when_indexed_columns_given(
        self, temp_catalog: Catalog
    ) -> None:
        """indexed_columns を渡すと json_extract(data, '$.col') が "col" に書き換えられる"""
        expr = Expr("json_extract(data, '$.source') = ?", ["EDINET"])
        got = Catalog._expr_to_inline_sql(expr, indexed_columns={"source"})
        assert got == "\"source\" = 'EDINET'"

    def test_replaces_multiple_placeholders_in_order(
        self, temp_catalog: Catalog
    ) -> None:
        """複数プレースホルダは expr.params の順で置換される"""
        expr = Expr("a = ? AND b = ?", ["x", 1])
        assert Catalog._expr_to_inline_sql(expr) == "a = 'x' AND b = 1"

    def test_expr_from_field_eq_builds_sql_with_placeholder(
        self, temp_catalog: Catalog
    ) -> None:
        """Field から生成した Expr を _expr_to_inline_sql するとリテラル埋め込み SQL になる"""
        expr = Field("source") == "EDGAR"
        # Field は indexed でない場合 json_extract(data, '$.source') = ? を生成
        got = Catalog._expr_to_inline_sql(expr)
        assert "?" not in got
        assert "'EDGAR'" in got


class TestCatalog_Helper_resolve_data_to_filing:
    """
    Catalog._resolve_data_to_filing のテスト
    - data から _filing_class を解決し Filing インスタンスを返す
    - 変換後には _filing_class を from_dict に渡す辞書から削除する
    """

    def test_returns_edinet_filing_when_filing_class_resolved(
        self, temp_catalog: Catalog, datetime_now: datetime
    ) -> None:
        """_filing_class が resolver で解決できる場合、そのクラスで復元される"""
        data: dict[str, Any] = {
            "_filing_class": "fino_filing.filing.filing_edinet.EDINETFiling",
            "id": "r_edinet_001",
            "source": "EDINET",
            "checksum": "a" * 64,
            "name": "f.txt",
            "is_zip": False,
            "format": "xbrl",
            "created_at": datetime_now.isoformat(),
            "doc_id": "doc1",
            "edinet_code": "E12345",
            "sec_code": "12345",
            "jcn": "1234567890123",
            "filer_name": "Test Inc.",
            "ordinance_code": "010",
            "form_code": "030101",
            "doc_type_code": "120",
            "doc_description": "有価証券報告書",
            "period_start": datetime_now.isoformat(),
            "period_end": datetime_now.isoformat(),
            "submit_datetime": datetime_now.isoformat(),
        }
        restored = temp_catalog._resolve_data_to_filing(data)
        assert isinstance(restored, EDINETFiling)
        assert restored.id == "r_edinet_001"
        assert restored.doc_id == "doc1"
        assert restored.filer_name == "Test Inc."

    def test_returns_filing_fallback_when_no_filing_class(
        self, temp_catalog: Catalog, datetime_now: datetime
    ) -> None:
        """_filing_class が無い場合、Filing で復元される"""
        data: dict[str, Any] = {
            "id": "r_base_001",
            "source": "test",
            "checksum": "b" * 64,
            "name": "f.txt",
            "is_zip": False,
            "format": "xbrl",
            "created_at": datetime_now.isoformat(),
        }
        restored = temp_catalog._resolve_data_to_filing(data)
        assert type(restored).__name__ == "Filing"
        assert restored.id == "r_base_001"
        assert restored.source == "test"

    def test_returns_filing_fallback_when_resolver_returns_none(
        self, temp_catalog: Catalog, datetime_now: datetime
    ) -> None:
        """_filing_class が resolver で解決できない場合、Filing にフォールバックする"""
        from fino_filing.collection.filing_resolver import FilingResolver

        class NoResolveResolver(FilingResolver):
            def resolve(self, name):  # type: ignore[no-untyped-def]
                return None

        # temp_catalogの一時ディレクトリだけ使うため
        catalog_path = temp_catalog.db_path
        temp_catalog.close()

        catalog = Catalog(catalog_path, resolver=NoResolveResolver())

        data: dict[str, Any] = {
            "_filing_class": "unknown.module.UnknownFiling",
            "id": "r_unknown_001",
            "source": "test",
            "checksum": "c" * 64,
            "name": "f.txt",
            "is_zip": False,
            "format": "xbrl",
            "created_at": datetime_now.isoformat(),
        }
        restored = catalog._resolve_data_to_filing(data)
        assert type(restored).__name__ == "Filing"
        assert restored.id == "r_unknown_001"
        catalog.close()

    def test_filing_class_removed_from_data_passed_to_from_dict(
        self, temp_catalog: Catalog, datetime_now: datetime
    ) -> None:
        """from_dict に渡す辞書には _filing_class が含まれない（pop で削除される）"""
        data: dict[str, Any] = {
            "_filing_class": "fino_filing.filing.filing.Filing",
            "id": "r_pop_001",
            "source": "test",
            "checksum": "d" * 64,
            "name": "f.txt",
            "is_zip": False,
            "format": "xbrl",
            "created_at": datetime_now.isoformat(),
        }
        restored = temp_catalog._resolve_data_to_filing(data)
        assert restored.id == "r_pop_001"
        assert not hasattr(restored, "_filing_class")

    def test_original_data_unchanged(
        self, temp_catalog: Catalog, datetime_now: datetime
    ) -> None:
        """呼び出し元の data 辞書は変更されない（内部でコピーしている）"""
        data: dict[str, Any] = {
            "_filing_class": "fino_filing.filing.filing.Filing",
            "id": "r_orig_001",
            "source": "test",
            "checksum": "e" * 64,
            "name": "f.txt",
            "is_zip": False,
            "format": "xbrl",
            "created_at": datetime_now.isoformat(),
        }
        temp_catalog._resolve_data_to_filing(data)
        assert "_filing_class" in data
        assert data["_filing_class"] == "fino_filing.filing.filing.Filing"
