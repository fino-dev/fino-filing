"""EdgerArchivesCollector / EdgerDocumentsCollector の取得戦略を検証する"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from fino_filing.collection.collection import Collection
from fino_filing.collector.base import RawDocument
from fino_filing.collector.edger import EdgerConfig
from fino_filing.collector.edger.archives.collector import (
    EdgerArchivesCollector,
    EdgerDocumentsCollector,
)
from fino_filing.collector.error import HttpNotFoundError


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edger
class TestEdgerArchivesCollector:
    """EdgerArchivesCollector Test"""

    def test_default_fetch_mode_is_primary(
        self,
        temp_collection: tuple[Collection, Any],
        edger_config: EdgerConfig,
    ) -> None:
        """デフォルト fetch_mode は primary（Arelle 向けの主文書優先）"""
        collection, _ = temp_collection
        collector = EdgerArchivesCollector(collection=collection, config=edger_config)
        assert collector._default_fetch_mode == "primary"

    def test_fetch_mode_override_per_collect(
        self,
        temp_collection: tuple[Collection, Any],
        edger_config: EdgerConfig,
    ) -> None:
        """collect 呼び出し時の fetch_mode がデフォルトより優先される"""
        collection, _ = temp_collection
        collector = EdgerArchivesCollector(collection=collection, config=edger_config)
        mock_client = MagicMock()
        mock_client.get_submissions.return_value = {
            "name": "Co",
            "filings": {
                "recent": {
                    "accessionNumber": ["0000320193-23-000106"],
                    "form": ["10-K"],
                    "filingDate": ["2023-10-27"],
                    "reportDate": ["2023-09-30"],
                    "primaryDocument": ["main.htm"],
                }
            },
        }
        mock_client.get_archives_file.return_value = b"<html/>"
        collector._client = mock_client

        list(
            collector._fetch_documents(
                cik_list=["320193"],
                limit_per_company=1,
                fetch_mode="filing_index",
            )
        )

        mock_client.get_archives_file.assert_called_with(
            "0000320193",
            "0000320193-23-000106",
            "0000320193-23-000106-index.htm",
        )

    class TestFetchDocumentsFilingIndex:
        """filing_index モードの _fetch_documents Test"""

        def test_yields_index_htm(
            self,
            temp_collection: tuple[Collection, Any],
            edger_config: EdgerConfig,
            edger_submissions_response_apple: dict[str, Any],
        ) -> None:
            """filing_index は各 accession の -index.htm を取得する"""
            collection, _ = temp_collection
            collector = EdgerArchivesCollector(
                collection=collection, config=edger_config, fetch_mode="filing_index"
            )
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edger_submissions_response_apple
            mock_client.get_archives_file.return_value = b"<html>index</html>"
            collector._client = mock_client

            rows = list(
                collector._fetch_documents(cik_list=["320193"], limit_per_company=1)
            )

            assert len(rows) == 1
            acc = edger_submissions_response_apple["filings"]["recent"][
                "accessionNumber"
            ][0]
            mock_client.get_archives_file.assert_called_once_with(
                "0000320193", acc, f"{acc}-index.htm"
            )
            assert rows[0].meta["primary_name"] == f"{acc}-index.htm"
            assert rows[0].meta["_origin"] == "archives"

    class TestFetchDocumentsPrimary:
        """primary モードの _fetch_documents Test"""

        def test_uses_submissions_primary_document(
            self,
            temp_collection: tuple[Collection, Any],
            edger_config: EdgerConfig,
            edger_submissions_response_apple: dict[str, Any],
        ) -> None:
            """Submissions の primaryDocument が取得できるときそれを使う"""
            collection, _ = temp_collection
            collector = EdgerArchivesCollector(
                collection=collection, config=edger_config, fetch_mode="primary"
            )
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = edger_submissions_response_apple
            mock_client.get_archives_file.return_value = b"<xml/>"
            collector._client = mock_client

            rows = list(
                collector._fetch_documents(cik_list=["320193"], limit_per_company=1)
            )

            assert len(rows) == 1
            expected_primary = edger_submissions_response_apple["filings"]["recent"][
                "primaryDocument"
            ][0]
            mock_client.get_archives_file.assert_called_once_with(
                "0000320193",
                edger_submissions_response_apple["filings"]["recent"][
                    "accessionNumber"
                ][0],
                expected_primary,
            )
            assert rows[0].meta["primary_name"] == expected_primary
            mock_client.get_filing_index_json.assert_not_called()

        def test_fallback_to_index_json_then_index_htm(
            self,
            temp_collection: tuple[Collection, Any],
            edger_config: EdgerConfig,
        ) -> None:
            """primary が 404 のあと index.json で本文を選び、だめなら index.htm"""
            collection, _ = temp_collection
            collector = EdgerArchivesCollector(
                collection=collection, config=edger_config, fetch_mode="primary"
            )
            acc = "0000320193-23-000106"
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = {
                "name": "Apple Inc.",
                "sic": "3571",
                "sicDescription": "Electronic Computers",
                "stateOfIncorporation": "CA",
                "fiscalYearEnd": "0926",
                "filings": {
                    "recent": {
                        "accessionNumber": [acc],
                        "form": ["10-K"],
                        "filingDate": ["2023-10-27"],
                        "reportDate": ["2023-09-30"],
                        "primaryDocument": ["missing.htm"],
                    }
                },
            }

            def archives_side_effect(_cik: str, _acc: str, name: str) -> bytes:
                if name == "missing.htm":
                    raise HttpNotFoundError("https://example/missing.htm")
                if name == "story.htm":
                    return b"<html>ix</html>"
                if name.endswith("-index.htm"):
                    return b"<html>idx</html>"
                raise AssertionError(f"unexpected file {name!r}")

            mock_client.get_archives_file.side_effect = archives_side_effect
            mock_client.get_filing_index_json.return_value = {
                "directory": {
                    "item": [
                        {"name": f"{acc}-index.htm"},
                        {"name": "story.htm"},
                    ]
                }
            }
            collector._client = mock_client

            rows = list(
                collector._fetch_documents(cik_list=["320193"], limit_per_company=1)
            )

            assert len(rows) == 1
            assert rows[0].content == b"<html>ix</html>"
            assert rows[0].meta["primary_name"] == "story.htm"
            mock_client.get_filing_index_json.assert_called_once()

        def test_fallback_to_index_htm_when_no_index_json(
            self,
            temp_collection: tuple[Collection, Any],
            edger_config: EdgerConfig,
        ) -> None:
            """primary 失敗かつ index.json 無しのとき -index.htm に落ちる"""
            collection, _ = temp_collection
            collector = EdgerArchivesCollector(
                collection=collection, config=edger_config, fetch_mode="primary"
            )
            acc = "0000320193-23-000106"
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = {
                "name": "Apple Inc.",
                "sic": "3571",
                "sicDescription": "",
                "stateOfIncorporation": "CA",
                "fiscalYearEnd": "0926",
                "filings": {
                    "recent": {
                        "accessionNumber": [acc],
                        "form": ["10-K"],
                        "filingDate": ["2023-10-27"],
                        "reportDate": ["2023-09-30"],
                        "primaryDocument": ["gone.htm"],
                    }
                },
            }

            def archives_side_effect(_cik: str, _acc: str, name: str) -> bytes:
                if name == "gone.htm":
                    raise HttpNotFoundError("https://example/gone.htm")
                if name == f"{acc}-index.htm":
                    return b"<html>toc</html>"
                raise AssertionError(f"unexpected file {name!r}")

            mock_client.get_archives_file.side_effect = archives_side_effect
            mock_client.get_filing_index_json.return_value = None
            collector._client = mock_client

            rows = list(
                collector._fetch_documents(cik_list=["320193"], limit_per_company=1)
            )

            assert len(rows) == 1
            assert rows[0].meta["primary_name"] == f"{acc}-index.htm"
            assert rows[0].content == b"<html>toc</html>"

    class TestFetchDocumentsXbrlBundle:
        """xbrl_bundle モードの _fetch_documents Test"""

        def test_yields_one_raw_per_matching_file(
            self,
            temp_collection: tuple[Collection, Any],
            edger_config: EdgerConfig,
        ) -> None:
            """index.json 上の xml/htm を個別 RawDocument として yield"""
            collection, _ = temp_collection
            collector = EdgerArchivesCollector(
                collection=collection, config=edger_config, fetch_mode="xbrl_bundle"
            )
            acc = "0000320193-23-000106"
            mock_client = MagicMock()
            mock_client.get_submissions.return_value = {
                "name": "Apple Inc.",
                "sic": "3571",
                "sicDescription": "",
                "stateOfIncorporation": "CA",
                "fiscalYearEnd": "0926",
                "filings": {
                    "recent": {
                        "accessionNumber": [acc],
                        "form": ["10-K"],
                        "filingDate": ["2023-10-27"],
                        "reportDate": ["2023-09-30"],
                        "primaryDocument": ["a.htm"],
                    }
                },
            }
            mock_client.get_filing_index_json.return_value = {
                "directory": {
                    "item": [
                        {"name": f"{acc}-index.htm"},
                        {"name": "b.xml"},
                        {"name": "c.htm"},
                    ]
                }
            }

            def archives_side_effect(_cik: str, _acc: str, name: str) -> bytes:
                return name.encode()

            mock_client.get_archives_file.side_effect = archives_side_effect
            collector._client = mock_client

            rows = list(
                collector._fetch_documents(cik_list=["320193"], limit_per_company=1)
            )

            assert len(rows) == 2
            names = [r.meta["primary_name"] for r in rows]
            assert names == ["b.xml", "c.htm"]
            assert isinstance(rows[0], RawDocument)


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edger
class TestEdgerDocumentsCollectorLegacy:
    """EdgerDocumentsCollector 後方互換 Test"""

    def test_defaults_to_filing_index(
        self,
        temp_collection: tuple[Collection, Any],
        edger_config: EdgerConfig,
    ) -> None:
        """旧クラスはデフォルトで filing_index（従来の index.htm のみ）"""
        collection, _ = temp_collection
        collector = EdgerDocumentsCollector(collection=collection, config=edger_config)
        assert collector._default_fetch_mode == "filing_index"
