"""Scenario: EdgarFactsCollector with mocked client (no SEC HTTP)."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from fino_filing import EdgarCompanyFactsFiling, Field
from fino_filing.collection.collection import Collection
from fino_filing.collector.edgar import EdgarConfig, EdgarFactsCollector


@pytest.mark.scenario
@pytest.mark.edgar
@pytest.mark.collector
class TestScenario_EdgarFactsCollectMocked:
    """Scenario: Edgar facts collect (mocked) Test"""

    def test_collect_facts_then_get_and_search(
        self,
        temp_collection_pair: tuple[Collection, Path],
        edgar_config: EdgarConfig,
        edgar_submissions_response_apple: dict[str, Any],
        edgar_company_facts_response_apple: dict[str, Any],
    ) -> None:
        """モック Client で Facts を収集し、Collection から get / search できる"""
        collection, _ = temp_collection_pair
        collector = EdgarFactsCollector(collection=collection, config=edgar_config)
        mock_client = MagicMock()
        mock_client.get_submissions.return_value = edgar_submissions_response_apple
        mock_client.get_company_facts.return_value = edgar_company_facts_response_apple
        collector._client = mock_client

        collected = collector.collect(cik_list=["320193"])
        assert len(collected) == 1
        filing, rel_path = collected[0]
        assert isinstance(filing, EdgarCompanyFactsFiling)
        assert filing.cik == "0000320193"
        assert Path(rel_path).name

        got_filing, content, path = collection.get(filing.id)
        assert got_filing is not None
        assert content is not None
        assert json.loads(content.decode()) == edgar_company_facts_response_apple
        assert path is not None

        rows = collection.search(
            expr=(Field("source") == EdgarCompanyFactsFiling.source), limit=10
        )
        assert len(rows) == 1
        assert rows[0].id == filing.id
