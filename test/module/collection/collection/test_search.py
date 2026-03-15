"""Collection.search の結合テスト。観点: 正常系（復元型）、expr 指定時のパラメータバインド"""

import hashlib
from datetime import datetime

import pytest

from fino_filing import Catalog, Collection, EDGARFiling, EDINETFiling, Field
from fino_filing.collection.storages import LocalStorage


@pytest.mark.module
@pytest.mark.collection
class TestCollection_Search_ReturnType:
    """Collection.search. 観点: 正常系（保存時の具象クラスで返る）"""

    def test_search_returns_edinet_filing_when_saved_as_edinet(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """EDINETFiling で add した場合、search で EDINETFiling として復元される"""
        content = b"test content"
        checksum = hashlib.sha256(content).hexdigest()
        edinet_filing = EDINETFiling(
            id="test_id_edinet_find",
            checksum=checksum,
            name="test_filing.txt",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
            doc_id="test_doc_id",
            edinet_code="test_edinet_code",
            sec_code="test_sec_code",
            jcn="test_jcn",
            filer_name="test_filer_name",
            ordinance_code="test_ordinance_code",
            form_code="test_form_code",
            doc_type_code="test_doc_type_code",
            doc_description="test_doc_description",
            period_start=datetime_now,
            period_end=datetime_now,
            submit_datetime=datetime_now,
        )
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        collection.add(edinet_filing, content)

        results = collection.search(limit=10)
        assert len(results) >= 1
        filing = next(f for f in results if f.id == edinet_filing.id)
        assert isinstance(filing, EDINETFiling)
        assert filing.edinet_code == edinet_filing.edinet_code
        assert filing.filer_name == edinet_filing.filer_name


@pytest.mark.module
@pytest.mark.collection
class TestCollection_Search_WithExpr:
    """
    Collection.search(expr=...) で Expr に文字列パラメータを渡した場合の検証。
    DuckDB が位置パラメータを結果セットの JSON 変換に誤用すると Conversion Error になるため、
    名前付きパラメータに変換する修正が効いていることを確認する。
    """

    def test_search_with_expr_source_returns_matching_filings_only(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """expr=(Field('source') == 'EDGAR') で検索すると EDGAR のみ返り、Conversion Error が発生しない"""
        content = b"content"
        checksum = hashlib.sha256(content).hexdigest()
        collection = Collection(storage=temp_storage, catalog=temp_catalog)

        edgar_filing = EDGARFiling(
            id="edgar_1",
            checksum=checksum,
            name="edgar.htm",
            is_zip=False,
            format="htm",
            created_at=datetime_now,
            cik="0000320193",
            accession_number="0000320193-23-000106",
            company_name="Apple Inc.",
            form_type="10-K",
            filing_date=datetime_now,
            period_of_report=datetime_now,
        )
        edinet_filing = EDINETFiling(
            id="edinet_1",
            checksum=checksum,
            name="edinet.pdf",
            is_zip=False,
            format="pdf",
            created_at=datetime_now,
            doc_id="S100XXX",
            edinet_code="E12345",
            sec_code="12345",
            jcn="1234567890123",
            filer_name="Test Inc.",
            ordinance_code="010",
            form_code="030000",
            doc_type_code="120",
            doc_description="有価証券報告書",
            period_start=datetime_now,
            period_end=datetime_now,
            submit_datetime=datetime_now,
        )
        collection.add(edgar_filing, content)
        collection.add(edinet_filing, content)

        results = collection.search(expr=(Field("source") == "EDGAR"), limit=10)
        assert len(results) == 1
        assert results[0].id == edgar_filing.id
        assert results[0].source == "EDGAR"
        assert isinstance(results[0], EDGARFiling)

    def test_search_with_expr_using_filing_class_source_same_as_string(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """Field('source') == EDGARFiling.source は Field('source') == 'EDGAR' と同一挙動（クラス参照でデフォルト値を返す）"""
        content = b"content"
        checksum = hashlib.sha256(content).hexdigest()
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        edgar_filing = EDGARFiling(
            id="edgar_1",
            checksum=checksum,
            name="f.htm",
            is_zip=False,
            format="htm",
            created_at=datetime_now,
            cik="0000320193",
            accession_number="0000320193-23-000106",
            company_name="Apple",
            form_type="10-K",
            filing_date=datetime_now,
            period_of_report=datetime_now,
        )
        collection.add(edgar_filing, content)

        by_string = collection.search(expr=(Field("source") == "EDGAR"), limit=10)
        by_class_default = collection.search(
            expr=(Field("source") == EDGARFiling.source), limit=10
        )
        assert len(by_string) == 1 and len(by_class_default) == 1
        assert by_string[0].id == by_class_default[0].id

    def test_count_with_expr_source(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """count(expr=(Field('source') == 'EDGAR')) が条件一致件数を返し、Conversion Error が発生しない"""
        content = b"content"
        checksum = hashlib.sha256(content).hexdigest()
        collection = Collection(storage=temp_storage, catalog=temp_catalog)

        for i, source in enumerate(["EDGAR", "EDINET", "EDGAR"]):
            if source == "EDGAR":
                f = EDGARFiling(
                    id=f"edgar_{i}",
                    checksum=checksum,
                    name="f.htm",
                    is_zip=False,
                    format="htm",
                    created_at=datetime_now,
                    cik="0000320193",
                    accession_number=f"0000320193-23-00010{i}",
                    company_name="Apple",
                    form_type="10-K",
                    filing_date=datetime_now,
                    period_of_report=datetime_now,
                )
            else:
                f = EDINETFiling(
                    id=f"edinet_{i}",
                    checksum=checksum,
                    name="f.pdf",
                    is_zip=False,
                    format="pdf",
                    created_at=datetime_now,
                    doc_id=f"S100{i}",
                    edinet_code="E1",
                    sec_code="1",
                    jcn="1",
                    filer_name="F",
                    ordinance_code="010",
                    form_code="030000",
                    doc_type_code="120",
                    doc_description="doc",
                    period_start=datetime_now,
                    period_end=datetime_now,
                    submit_datetime=datetime_now,
                )
            collection.add(f, content)

        n = temp_catalog.count(expr=(Field("source") == "EDGAR"))
        assert n == 2
