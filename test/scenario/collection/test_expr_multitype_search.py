"""Scenario: Field / Expr search across multiple Filing types."""

from __future__ import annotations

import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterator

import pytest
from scenario.support.scenario_custom_filing import ScenarioDeskFiling  # noqa: E402

from fino_filing import (
    Catalog,
    Collection,
    EdgarCompanyFactsFiling,
    EDINETFiling,
    Field,
    Filing,
    FilingResolver,
    LocalStorage,
)
from fino_filing.util.content import sha256_checksum


def _multitype_resolver() -> FilingResolver:
    r = FilingResolver()
    r.register(Filing)
    r.register(EDINETFiling)
    r.register(EdgarCompanyFactsFiling)
    r.register(ScenarioDeskFiling)
    return r


@pytest.fixture
def multitype_collection() -> Iterator[Collection]:
    with tempfile.TemporaryDirectory(prefix="scenario_expr_") as tmpdir:
        base = Path(tmpdir)
        catalog = Catalog(str(base / "index.db"), resolver=_multitype_resolver())
        storage = LocalStorage(base / "storage")
        collection = Collection(storage=storage, catalog=catalog)
        yield collection
        catalog.close()


@pytest.mark.scenario
@pytest.mark.collection
@pytest.mark.field
class TestScenario_ExprMultitypeSearch:
    """Scenario: Expr and Field across filing types Test"""

    def test_in_or_model_field_contains_not_limit_offset(
        self, multitype_collection: Collection
    ) -> None:
        """in_ / OR / 型固有 Field / contains / NOT / limit・offset・order_by を一通り使える"""
        c = multitype_collection
        t0 = datetime(2024, 1, 1, 12, 0, 0)

        content_edinet = b"<xbrl/>"
        ch_edinet = sha256_checksum(content_edinet)
        edinet = EDINETFiling(
            id="sc-edinet-1",
            checksum=ch_edinet,
            name="annual_report.xbrl",
            is_zip=False,
            format="xbrl",
            created_at=t0,
            doc_id="S100MULTI",
            edinet_code="E11111",
            sec_code="1111",
            jcn="1111111111111",
            filer_name="Multi 提出者",
            fund_code="F1",
            ordinance_code="010",
            form_code="030000",
            doc_type_code="120",
            doc_description="有報",
            period_start=date(2023, 4, 1),
            period_end=date(2024, 3, 31),
            submit_datetime=t0,
            current_report_reason="",
            parent_doc_id=None,
        )

        content_facts = b'{"facts": true}'
        ch_facts = sha256_checksum(content_facts)
        facts = EdgarCompanyFactsFiling(
            id="sc-facts-1",
            checksum=ch_facts,
            name=EdgarCompanyFactsFiling.build_default_name("1652044"),
            is_zip=False,
            format="json",
            created_at=t0 + timedelta(seconds=1),
            cik="0001652044",
            entity_type="operating",
            filer_name="Alphabet Inc.",
            sic="7370",
            sic_description="Services",
            filer_category="Large accelerated filer",
            state_of_incorporation="DE",
            fiscal_year_end="12-31",
            tickers_key="GOOGL",
            exchanges_key="Nasdaq",
        )

        content_desk = b"desk-memo"
        ch_desk = sha256_checksum(content_desk)
        desk = ScenarioDeskFiling(
            id="sc-desk-1",
            source="DESK",
            checksum=ch_desk,
            name="quarterly_report_memo.txt",
            is_zip=False,
            format="txt",
            created_at=t0 + timedelta(seconds=2),
            portfolio_code="ALPHA",
            desk_tag="eod",
        )

        content_int = b"internal"
        ch_int = sha256_checksum(content_int)
        internal = Filing(
            id="sc-internal-1",
            source="INTERNAL",
            checksum=ch_int,
            name="internal.csv",
            is_zip=False,
            format="csv",
            created_at=t0 + timedelta(seconds=3),
        )

        c.add(edinet, content_edinet)
        c.add(facts, content_facts)
        c.add(desk, content_desk)
        c.add(internal, content_int)

        sources = Field("source").in_(["EDINET", "EDGAR", "DESK", "INTERNAL"])
        all_four = c.search(expr=sources, limit=10, order_by="created_at", desc=False)
        assert len(all_four) == 4

        or_edinet_edgar = c.search(
            expr=(Field("source") == "EDINET") | (Field("source") == "EDGAR"),
            limit=10,
            order_by="created_at",
            desc=False,
        )
        assert len(or_edinet_edgar) == 2
        assert {f.id for f in or_edinet_edgar} == {"sc-edinet-1", "sc-facts-1"}

        by_cik = c.search(expr=(EdgarCompanyFactsFiling.cik == "0001652044"), limit=10)
        assert len(by_cik) == 1
        assert isinstance(by_cik[0], EdgarCompanyFactsFiling)

        by_name = c.search(expr=Field("name").contains("report"), limit=10)
        assert {f.id for f in by_name} == {"sc-edinet-1", "sc-desk-1"}

        not_internal = c.search(expr=~(Field("source") == "INTERNAL"), limit=10)
        assert len(not_internal) == 3
        assert all(f.source != "INTERNAL" for f in not_internal)

        paged_a = Filing(
            id="pg-a",
            source="PAGED",
            checksum=sha256_checksum(b"a"),
            name="doc_m.txt",
            is_zip=False,
            format="txt",
            created_at=t0 + timedelta(seconds=10),
        )
        paged_b = Filing(
            id="pg-b",
            source="PAGED",
            checksum=sha256_checksum(b"b"),
            name="doc_n.txt",
            is_zip=False,
            format="txt",
            created_at=t0 + timedelta(seconds=11),
        )
        paged_c = Filing(
            id="pg-c",
            source="PAGED",
            checksum=sha256_checksum(b"c"),
            name="doc_o.txt",
            is_zip=False,
            format="txt",
            created_at=t0 + timedelta(seconds=12),
        )
        paged_d = Filing(
            id="pg-d",
            source="PAGED",
            checksum=sha256_checksum(b"d"),
            name="doc_p.txt",
            is_zip=False,
            format="txt",
            created_at=t0 + timedelta(seconds=13),
        )
        c.add(paged_a, b"a")
        c.add(paged_b, b"b")
        c.add(paged_c, b"c")
        c.add(paged_d, b"d")

        page = c.search(
            expr=Field("source") == "PAGED",
            limit=2,
            offset=1,
            order_by="name",
            desc=False,
        )
        assert [f.name for f in page] == ["doc_n.txt", "doc_o.txt"]
