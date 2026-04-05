import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from fino_filing import Collection, EdgarArchiveCollector, EdgarConfig
from fino_filing.collector.edgar.archive.enum import EdgarDocumentsFetchMode
from fino_filing.collector.error import CollectorParseResponseValidationError


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edgar
class TestEdgarArchiveCollector:
    """
    EdgarArchiveCollector Test
    """

    def test_collector_initialize_with_config(
        self,
        temp_collection: tuple[Collection, Path],
        edgar_config: EdgarConfig,
    ) -> None:
        """Collector の初期化が config を渡して client に反映される"""
        collection, _ = temp_collection
        collector = EdgarArchiveCollector(collection=collection, config=edgar_config)
        assert collector._client._headers["User-Agent"] == "test@example.com"

    def test_fetch_mode_primary_only_uses_archives_file(
        self,
        temp_collection: tuple[Collection, Path],
        edgar_config: EdgarConfig,
        edgar_submissions_response_apple: dict[str, Any],
    ) -> None:
        """fetch_mode=primary_only で primaryDocument パスを get_archives_file する"""
        collection, _ = temp_collection
        collector = EdgarArchiveCollector(collection=collection, config=edgar_config)
        mock_client = MagicMock()
        mock_client.get_submissions.return_value = edgar_submissions_response_apple
        mock_client.get_archives_file.return_value = b"<p>primary</p>"
        collector._client = mock_client

        out = collector.collect(
            cik_list=["0000320193"],
            limit_per_company=1,
            fetch_mode=EdgarDocumentsFetchMode.PRIMARY_ONLY,
        )

        assert len(out) == 1
        filing, _path = out[0]
        assert filing.format == "xml"
        assert filing.is_zip is False
        mock_client.get_archives_file.assert_called_once()
        call = mock_client.get_archives_file.call_args
        assert call[0][2] == "xslSCHEDULE_13G_X02/primary_doc.xml"

    def test_fetch_mode_full_builds_zip(
        self,
        temp_collection: tuple[Collection, Path],
        edgar_config: EdgarConfig,
        edgar_submissions_response_apple: dict[str, Any],
    ) -> None:
        """fetch_mode=full で index 由来の全ファイルを ZIP にまとめる"""
        collection, _ = temp_collection
        collector = EdgarArchiveCollector(collection=collection, config=edgar_config)
        mock_client = MagicMock()
        mock_client.get_submissions.return_value = edgar_submissions_response_apple
        mock_client.try_get_filing_index_json.return_value = {
            "directory": {
                "item": [
                    {"name": "a.htm", "type": "text.gif", "size": "1"},
                    {"name": "b.xml", "type": "text.gif", "size": "2"},
                ]
            }
        }

        def _archives_side_effect(_cik: str, _acc: str, rel: str, **_k: Any) -> bytes:
            return rel.encode()

        mock_client.get_archives_file.side_effect = _archives_side_effect
        collector._client = mock_client

        out = collector.collect(
            cik_list=["0000320193"],
            limit_per_company=1,
            fetch_mode=EdgarDocumentsFetchMode.FULL,
        )

        assert len(out) == 1
        filing, _path = out[0]
        assert filing.format == "zip"
        assert filing.is_zip is True
        stored = collection.get_content(filing.id)
        assert stored is not None
        zf = zipfile.ZipFile(BytesIO(stored), "r")
        assert set(zf.namelist()) == {"a.htm", "b.xml"}
        assert zf.read("a.htm") == b"a.htm"

    def test_filings_recent_length_mismatch_raises(
        self,
        temp_collection: tuple[Collection, Path],
        edgar_config: EdgarConfig,
        edgar_submissions_response_apple: dict[str, Any],
    ) -> None:
        """primary_only で並列配列の長さが揃わないとき検証エラーとする"""
        collection, _ = temp_collection
        collector = EdgarArchiveCollector(collection=collection, config=edgar_config)
        bad = {**edgar_submissions_response_apple}
        recent = dict(bad["filings"]["recent"])
        recent["primaryDocument"] = recent["primaryDocument"][:-1]
        bad["filings"]["recent"] = recent
        mock_client = MagicMock()
        mock_client.get_submissions.return_value = bad
        collector._client = mock_client

        with pytest.raises(CollectorParseResponseValidationError):
            collector.collect(
                cik_list=["0000320193"],
                fetch_mode="primary_only",
            )
