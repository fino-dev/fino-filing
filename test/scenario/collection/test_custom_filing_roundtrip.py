"""Scenario: custom Filing subclass — register, add, search, get."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pytest
from scenario.support.scenario_custom_filing import ScenarioDeskFiling  # noqa: E402

from fino_filing import Catalog, Collection, Field, FilingResolver, LocalStorage
from fino_filing.util.content import sha256_checksum


@pytest.fixture
def desk_collection() -> Iterator[Collection]:
    r = FilingResolver()
    r.register(ScenarioDeskFiling)
    with tempfile.TemporaryDirectory(prefix="scenario_desk_") as tmpdir:
        base = Path(tmpdir)
        catalog = Catalog(str(base / "index.db"), resolver=r)
        storage = LocalStorage(base / "storage")
        collection = Collection(storage=storage, catalog=catalog)
        yield collection
        catalog.close()


@pytest.mark.scenario
@pytest.mark.collection
@pytest.mark.filing
class TestScenario_CustomFilingRoundtrip:
    """Scenario: Custom Filing register and roundtrip Test"""

    def test_add_search_get_restores_subclass(
        self, desk_collection: Collection
    ) -> None:
        """default_resolver 以外の resolver で登録したサブクラスが get で復元される"""
        content = b"desk-payload-xyz"
        checksum = sha256_checksum(content)
        created = datetime(2024, 7, 1, 15, 30, 0)
        filing = ScenarioDeskFiling(
            id="desk-roundtrip-1",
            source="DESK",
            checksum=checksum,
            name="memo_portfolio_a.txt",
            is_zip=False,
            format="txt",
            created_at=created,
            portfolio_code="PF-777",
            desk_tag="gamma",
        )

        _, rel = desk_collection.add(filing, content)
        assert rel

        rows = desk_collection.search(
            expr=(Field("portfolio_code") == "PF-777") & (Field("desk_tag") == "gamma"),
            limit=10,
        )
        assert len(rows) == 1
        assert isinstance(rows[0], ScenarioDeskFiling)
        assert rows[0].portfolio_code == "PF-777"

        got_filing, got_bytes, path = desk_collection.get("desk-roundtrip-1")
        assert isinstance(got_filing, ScenarioDeskFiling)
        assert got_filing.desk_tag == "gamma"
        assert got_bytes == content
        assert path is not None
