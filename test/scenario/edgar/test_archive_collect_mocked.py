"""Scenario: EdgarArchiveCollector with mocked client (no SEC HTTP)."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from fino_filing import EdgarArchiveFiling, Field
from fino_filing.collection.collection import Collection
from fino_filing.collector.edgar import EdgarArchiveCollector, EdgarConfig


@pytest.mark.scenario
@pytest.mark.edgar
@pytest.mark.collector
class TestScenario_EdgarArchiveCollectMocked:
    """Scenario: Edgar archive collect (mocked) Test"""

    def test_collect_primary_document_then_get_and_search(
        self,
        temp_collection_pair: tuple[Collection, Path],
        edgar_config: EdgarConfig,
        edgar_submissions_response_apple: dict[str, Any],
    ) -> None:
        """モック Client でアーカイブ本文を収集し、Collection から get / search できる"""
        collection, _ = temp_collection_pair
        collector = EdgarArchiveCollector(collection=collection, config=edgar_config)
        mock_client = MagicMock()
        mock_client.get_submissions.return_value = edgar_submissions_response_apple
        primary_bytes = b"<?xml version='1.0'?><primary/>"
        mock_client.get_archives_file.return_value = primary_bytes
        collector._client = mock_client

        collected = collector.collect(cik_list=["320193"], limit_per_company=1)
        assert len(collected) == 1
        filing, rel_path = collected[0]
        assert isinstance(filing, EdgarArchiveFiling)
        assert filing.cik == "0000320193"
        assert Path(rel_path).name

        got_filing, content, path = collection.get(filing.id)
        assert got_filing is not None
        assert content == primary_bytes
        assert path is not None

        rows = collection.search(
            expr=(Field("source") == EdgarArchiveFiling.source), limit=10
        )
        assert len(rows) == 1
        assert rows[0].id == filing.id
