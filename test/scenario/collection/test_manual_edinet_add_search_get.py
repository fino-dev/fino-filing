"""Scenario: manual EDINET filing into Collection (matches Basic usage in docs)."""

from datetime import date, datetime
from pathlib import Path

import pytest

from fino_filing import EDINETFiling, Field
from fino_filing.collection.collection import Collection
from fino_filing.util.content import sha256_checksum


@pytest.mark.scenario
@pytest.mark.collection
class TestScenario_ManualEdinetAddSearchGet:
    """Scenario: Manual EDINET add, search, and get Test"""

    def test_manual_add_then_search_get_and_content(
        self, temp_collection: Collection
    ) -> None:
        """手動で EDINETFiling を add し、search / get / get_content で取得できる"""
        content = b"<?xml version='1.0'?><xbrl>scenario</xbrl>"
        checksum = sha256_checksum(content)
        created = datetime(2024, 6, 1, 12, 0, 0)
        filing = EDINETFiling(
            id="scenario_edinet_001",
            checksum=checksum,
            name="scenario_edinet_001.xbrl",
            is_zip=False,
            format="xbrl",
            created_at=created,
            doc_id="S100SCENARIO",
            edinet_code="E00000",
            sec_code="0000",
            jcn="0000000000000",
            filer_name="Scenario Corp",
            fund_code="F000",
            ordinance_code="010",
            form_code="030000",
            doc_type_code="120",
            doc_description="有価証券報告書",
            period_start=date(2023, 4, 1),
            period_end=date(2024, 3, 31),
            submit_datetime=datetime(2024, 6, 1, 9, 0),
            current_report_reason="",
            parent_doc_id=None,
        )

        stored, rel_path = temp_collection.add(filing, content)
        assert stored.id == filing.id
        assert Path(rel_path).name

        rows = temp_collection.search(expr=(Field("source") == "EDINET"), limit=10)
        assert len(rows) == 1
        assert rows[0].id == filing.id
        assert isinstance(rows[0], EDINETFiling)

        meta = temp_collection.get_filing(filing.id)
        assert meta is not None
        assert meta.doc_id == "S100SCENARIO"

        raw = temp_collection.get_content(filing.id)
        assert raw == content

        got_filing, got_content, path = temp_collection.get(filing.id)
        assert got_filing is not None
        assert got_content == content
        assert path is not None
        assert Path(path).is_file()

        same_source = temp_collection.search(
            expr=(EDINETFiling.source == "EDINET"), limit=10
        )
        assert len(same_source) == 1 and same_source[0].id == filing.id

        # Expr 結合の例（シナリオとして1本に含める）
        combined = temp_collection.search(
            expr=(Field("source") == "EDINET") & (Field("doc_id") == "S100SCENARIO"),
            limit=10,
        )
        assert len(combined) == 1
