"""Scenario: EdinetCollector with mocked client (no EDINET HTTP)."""

from datetime import date
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from fino_filing import EDINETFiling, Field
from fino_filing.collection.collection import Collection
from fino_filing.collector.edinet import EdinetCollector, EdinetConfig
from fino_filing.collector.edinet.enum import EDINET_DOCUMENT_DOWNLOAD_TYPE


@pytest.mark.scenario
@pytest.mark.edinet
@pytest.mark.collector
class TestScenario_EdinetCollectMocked:
    """Scenario: EDINET collect (mocked) Test"""

    def test_collect_one_document_then_get_and_search(
        self,
        temp_collection_pair: tuple[Collection, Path],
        tmp_edinet_config: EdinetConfig,
        edinet_document_list_response_type2_5_items: dict[str, Any],
    ) -> None:
        """モック Client で1件収集し、Collection から get / search できる"""
        collection, _ = temp_collection_pair
        collector = EdinetCollector(collection=collection, config=tmp_edinet_config)
        mock_client = MagicMock()
        mock_client.get_document_list.return_value = (
            edinet_document_list_response_type2_5_items
        )
        mock_client.get_document.return_value = b"%PDF-1.4 scenario"
        collector._client = mock_client

        collected = collector.collect(
            date_from=date(2025, 4, 2),
            date_to=date(2025, 4, 2),
            document_type=EDINET_DOCUMENT_DOWNLOAD_TYPE.PDF,
            limit=1,
        )
        assert len(collected) == 1
        filing, rel_path = collected[0]
        assert isinstance(filing, EDINETFiling)
        assert filing.doc_id == "S100VIZF"
        assert Path(rel_path).name

        got_filing, content, path = collection.get(filing.id)
        assert got_filing is not None
        assert content == b"%PDF-1.4 scenario"
        assert path is not None

        rows = collection.search(expr=(Field("source") == "EDINET"), limit=10)
        assert len(rows) == 1
        assert rows[0].id == filing.id
