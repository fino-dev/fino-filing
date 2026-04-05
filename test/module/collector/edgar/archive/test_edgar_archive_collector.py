"""EdgarArchiveCollector の collect フローと RawDocument / Filing 連携を検証する"""

import zipfile
from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from fino_filing import Collection, EdgarArchiveFiling
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edgar import (
    EdgarArchiveCollector,
    EdgarConfig,
)
from fino_filing.collector.edgar.archive.enum import EdgarDocumentsFetchMode
from fino_filing.collector.error import (
    CollectorNoContentError,
    CollectorParseResponseValidationError,
)
from fino_filing.util.content import sha256_checksum


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edgar
class TestEdgarArchiveCollector:
    """EdgarArchiveCollector Test"""

    def test_collector_initialize_with_config(
        self,
        temp_collection: tuple[Collection, Path],
        edgar_config: EdgarConfig,
    ) -> None:
        """Collector の初期化が config を渡して client に反映される"""
        collection, _ = temp_collection
        collector = EdgarArchiveCollector(collection=collection, config=edgar_config)
        assert collector._client._headers["User-Agent"] == "test@example.com"

    class TestFetchDocuments:
        """EdgarArchiveCollector._fetch_documents Test"""

        def test_fetch_documents_returns_raw_documents(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
        ) -> None:
            """
            Submissions とアーカイブ本文が取得できる場合、会社・提出メタを付与した RawDocument を yield する。
            """
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edgar_submissions_response_apple
            primary_bytes = b"<?xml version='1.0'?><root/>"
            mock_client.get_archives_file.return_value = primary_bytes
            collector._client = mock_client

            results = list(
                collector._fetch_documents(
                    cik_list=["320193"],
                    limit_per_company=1,
                )
            )

            assert len(results) == 1
            mock_client.get_submissions.assert_called_once_with("0000320193")
            mock_client.get_archives_file.assert_called_once_with(
                "0000320193",
                "0000102909-26-000630",
                "xslSCHEDULE_13G_X02/primary_doc.xml",
            )
            assert isinstance(results[0], RawDocument)
            assert results[0].content == primary_bytes
            assert results[0].meta["cik"] == "0000320193"
            assert results[0].meta["entityType"] == "operating"
            assert results[0].meta["name"] == "Apple Inc."
            assert results[0].meta["accessionNumber"] == "0000102909-26-000630"
            assert results[0].meta["form"] == "SCHEDULE 13G/A"
            assert results[0].meta["primaryDocument"] == (
                "xslSCHEDULE_13G_X02/primary_doc.xml"
            )
            assert (
                results[0].meta["_fetch_mode"] == EdgarDocumentsFetchMode.PRIMARY_ONLY
            )

        def test_fetch_documents_returns_empty_iterator(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """cik_list が空のとき _fetch_documents は要素を yield しない"""
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            assert list(collector._fetch_documents(cik_list=[])) == []

        def test_fetch_documents_raises_when_no_submissions(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """Submissions が空のとき CollectorNoContentError を送出する"""
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = {}
            collector._client = mock_client

            with pytest.raises(CollectorNoContentError) as exc:
                list(collector._fetch_documents(cik_list=["0000320193"]))
            assert exc.value.content_id == "0000320193"

        def test_fetch_documents_raises_when_primary_document_missing(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
        ) -> None:
            """primaryDocument が空のとき CollectorNoContentError を送出する"""
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            payload = {**edgar_submissions_response_apple}
            recent = dict(payload["filings"]["recent"])
            recent["primaryDocument"] = [""] + recent["primaryDocument"][1:]
            payload["filings"] = {"recent": recent}
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = payload
            collector._client = mock_client

            with pytest.raises(CollectorNoContentError):
                list(
                    collector._fetch_documents(
                        cik_list=["320193"],
                        limit_per_company=1,
                    )
                )

        def test_fetch_documents_raises_when_archives_empty(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
        ) -> None:
            """PRIMARY_ONLY でprimaryDocument取得が空のとき CollectorNoContentError を送出する"""
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edgar_submissions_response_apple
            mock_client.get_archives_file.return_value = b""
            collector._client = mock_client

            with pytest.raises(CollectorNoContentError):
                list(
                    collector._fetch_documents(
                        cik_list=["320193"],
                        limit_per_company=1,
                    )
                )

        def test_fetch_documents_respects_limit_per_company(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
        ) -> None:
            """limit_per_company が指定された件数だけアーカイブ取得する"""
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edgar_submissions_response_apple
            mock_client.get_archives_file.return_value = b"x"
            collector._client = mock_client

            results = list(
                collector._fetch_documents(
                    cik_list=["320193"],
                    limit_per_company=2,
                )
            )
            assert len(results) == 2
            assert mock_client.get_archives_file.call_count == 2

        def test_fetch_documents_full_mode_fetches_zip_from_index(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
        ) -> None:
            """
            FULL モードで index.json に zip が列挙されるとき、その zip バイト列を本文とする。
            """
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            buf = BytesIO()
            with zipfile.ZipFile(buf, "w") as zf:
                zf.writestr("a.txt", b"sec")
            zip_bytes = buf.getvalue()

            index_obj: dict[str, Any] = {
                "directory": {
                    "item": {
                        "name": "complete-submission.zip",
                        "type": "text.gif",
                        "size": "1",
                    }
                }
            }
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edgar_submissions_response_apple
            mock_client.try_get_filing_index_json.return_value = index_obj
            mock_client.get_archives_file.return_value = zip_bytes
            collector._client = mock_client

            results = list(
                collector._fetch_documents(
                    cik_list=["320193"],
                    limit_per_company=1,
                    fetch_mode=EdgarDocumentsFetchMode.FULL,
                )
            )

            assert len(results) == 1
            mock_client.try_get_filing_index_json.assert_called_once_with(
                "0000320193",
                "0000102909-26-000630",
            )
            mock_client.get_archives_file.assert_called_once_with(
                "0000320193",
                "0000102909-26-000630",
                "complete-submission.zip",
            )
            assert results[0].content == zip_bytes
            assert results[0].meta["_fetch_mode"] == EdgarDocumentsFetchMode.FULL

    class TestParseResponse:
        """EdgarArchiveCollector._parse_response Test"""

        def test_parse_response_normalizes_meta(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
        ) -> None:
            """EdgarArchiveCollector._parse_response が会社・提出メタを正規化する"""
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edgar_submissions_response_apple
            mock_client.get_archives_file.return_value = b"<x/>"
            collector._client = mock_client

            raw = next(
                collector._fetch_documents(
                    cik_list=["320193"],
                    limit_per_company=1,
                )
            )
            parsed = collector._parse_response(
                RawDocument(content=raw.content, meta=raw.meta)
            )
            assert parsed["cik"] == "0000320193"
            assert parsed["entity_type"] == "operating"
            assert parsed["filer_name"] == "Apple Inc."
            assert parsed["sic"] == "3571"
            assert parsed["accession_number"] == "0000102909-26-000630"
            assert parsed["filing_date"] == date(2026, 3, 26)
            assert parsed["report_date"] is None
            assert parsed["acceptance_date_time"] == datetime(2026, 3, 26, 19, 43, 19)
            assert parsed["form"] == "SCHEDULE 13G/A"
            assert parsed["is_xbrl"] is False
            assert parsed["is_inline_xbrl"] is False
            assert parsed["primary_document"] == ("xslSCHEDULE_13G_X02/primary_doc.xml")
            assert parsed["_fetch_mode"] == EdgarDocumentsFetchMode.PRIMARY_ONLY

    class TestBuildFiling:
        """EdgarArchiveCollector._build_filing Test"""

        def test_build_filing_normalizes_filing(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
            edgar_submissions_response_apple: dict[str, Any],
        ) -> None:
            """EdgarArchiveCollector._build_filing が EdgarArchiveFiling を組み立てる"""
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edgar_submissions_response_apple
            body = b"<?xml version='1.0'?><form4/>"
            mock_client.get_archives_file.return_value = body
            collector._client = mock_client

            it = collector._fetch_documents(
                cik_list=["320193"],
                limit_per_company=2,
            )
            _first = next(it)
            raw = next(it)

            parsed = collector._parse_response(
                RawDocument(content=raw.content, meta=raw.meta)
            )
            filing = collector._build_filing(parsed, raw.content)
            assert isinstance(filing, EdgarArchiveFiling)
            assert filing.source == "EDGAR"
            assert filing.name == EdgarArchiveFiling.build_default_name(
                cik="0000320193",
                accession="0001780525-26-000005",
                fetch_mode=EdgarDocumentsFetchMode.PRIMARY_ONLY,
                format="xml",
                is_zip=False,
            )
            assert filing.checksum == sha256_checksum(body)
            assert filing.format == "xml"
            assert not filing.is_zip
            assert filing.cik == "0000320193"
            assert filing.accession_number == "0001780525-26-000005"
            assert filing.entity_type == "operating"
            assert filing.filer_name == "Apple Inc."
            assert filing.sic == "3571"
            assert filing.filing_date == date(2026, 3, 17)
            assert filing.report_date == date(2026, 3, 15)
            assert filing.acceptance_date_time == datetime(2026, 3, 17, 22, 31, 17)
            assert filing.form == "4"
            assert filing.primary_document == "xslF345X05/wk-form4_1773786674.xml"
            assert filing.primary_doc_description == "FORM 4"
            assert filing.tickers_key == "AAPL"
            assert filing.exchanges_key == "Nasdaq"

        def test_build_filing_requires_cik(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """cik が無い Parsed に対して CollectorParseResponseValidationError を送出する"""
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            with pytest.raises(CollectorParseResponseValidationError) as exc:
                collector._build_filing(
                    {
                        "accession_number": "0000320193-26-000001",
                        "_fetch_mode": EdgarDocumentsFetchMode.PRIMARY_ONLY,
                    },
                    b"x",
                )
            assert exc.value.field == "cik"

        def test_build_filing_requires_accession_number(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """accession_number が無いとき CollectorParseResponseValidationError を送出する"""
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            with pytest.raises(CollectorParseResponseValidationError) as exc:
                collector._build_filing(
                    {
                        "cik": "0000320193",
                        "_fetch_mode": EdgarDocumentsFetchMode.PRIMARY_ONLY,
                    },
                    b"x",
                )
            assert exc.value.field == "accession_number"

        def test_build_filing_requires_fetch_mode(
            self,
            temp_collection: tuple[Collection, Path],
            edgar_config: EdgarConfig,
        ) -> None:
            """_fetch_mode が EdgarDocumentsFetchMode でないとき CollectorParseResponseValidationError を送出する"""
            collection, _ = temp_collection
            collector = EdgarArchiveCollector(
                collection=collection, config=edgar_config
            )
            with pytest.raises(CollectorParseResponseValidationError) as exc:
                collector._build_filing(
                    {
                        "cik": "0000320193",
                        "accession_number": "0000320193-26-000001",
                        "_fetch_mode": "primary",
                    },
                    b"x",
                )
            assert exc.value.field == "fetch_mode"
