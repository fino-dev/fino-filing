from datetime import date, datetime

import pytest

from fino_filing.collector.edgar._helper import (
    _accession_to_dir,
    _filenames_from_sec_index_json,
    _infer_edgar_archive_format,
    _parse_edgar_date,
    _parse_edgar_datetime,
    _parse_edgar_flag,
    _verify_and_parse_edgar_submissions_recent_filings,
)
from fino_filing.collector.error import CollectorParseResponseValidationError


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edgar
class TestEdgarHelper:
    class TestAccessionToDir:
        """_accession_to_dir"""

        def test_accession_to_dir_success(self) -> None:
            """accession_to_dir が正常に動作する"""
            assert _accession_to_dir("0000320193-23-000106") == "000032019323000106"

    class TestParseEdgarDate:
        """_parse_edgar_date"""

        def test_parse_edgar_date_success(self) -> None:
            """parse_edgar_date が正常に動作する"""
            assert _parse_edgar_date("2026-04-05") == date(2026, 4, 5)

    class TestParseEdgarDatetime:
        """_parse_edgar_datetime"""

        def test_parse_edgar_datetime_success(self) -> None:
            """Z 付きは UTC の naive datetime に正規化される"""
            assert _parse_edgar_datetime("2026-04-05T12:00:00.000Z") == datetime(
                2026, 4, 5, 12, 0, 0
            )

        def test_parse_edgar_datetime_offset_to_utc_naive(self) -> None:
            """オフセット付きは UTC に換算して tzinfo を落とす"""
            assert _parse_edgar_datetime("2026-04-05T12:00:00+09:00") == datetime(
                2026, 4, 5, 3, 0, 0
            )

    class TestParseEdgarFlag:
        """_parse_edgar_flag"""

        def test_parse_edgar_flag_success(self) -> None:
            """parse_edgar_flag が正常に動作する"""
            assert not _parse_edgar_flag("0")
            assert _parse_edgar_flag("1")
            assert not _parse_edgar_flag(0)
            assert _parse_edgar_flag(1)
            assert _parse_edgar_flag("") is None
            assert _parse_edgar_flag(None) is None
            assert _parse_edgar_flag("2") is None
            assert _parse_edgar_flag(2) is None

    class TestInferEdgarFormat:
        """_infer_edgar_archive_format"""

        def test_infer_edgar_archive_format_success(self) -> None:
            """infer_edgar_format が正常に動作する"""
            assert (
                _infer_edgar_archive_format(
                    is_xbrl=True, is_inline_xbrl=False, primary_document=None
                )
                == "xbrl"
            )
            assert (
                _infer_edgar_archive_format(
                    is_xbrl=False, is_inline_xbrl=True, primary_document=None
                )
                == "ixbrl"
            )
            assert (
                _infer_edgar_archive_format(
                    is_xbrl=False, is_inline_xbrl=False, primary_document="a.htm"
                )
                == "htm"
            )
            assert (
                _infer_edgar_archive_format(
                    is_xbrl=False, is_inline_xbrl=False, primary_document="a.xml"
                )
                == "xml"
            )
            assert (
                _infer_edgar_archive_format(
                    is_xbrl=False, is_inline_xbrl=False, primary_document=None
                )
                == "htm"
            )

    class TestIndexJsonAndHtm:
        def test_filenames_from_sec_index_json_single_item_object(self) -> None:
            """index.json の item が単一オブジェクトのときも列挙できる"""
            raw = {
                "directory": {
                    "item": {
                        "name": "a.htm",
                        "type": "text.gif",
                        "size": "1",
                    }
                }
            }
            assert _filenames_from_sec_index_json(raw) == ["a.htm"]

        def test_filenames_from_sec_index_json_multiple_item_object(self) -> None:
            """index.json の item が複数オブジェクトのときも列挙できる"""
            raw = {
                "directory": {
                    "item": [
                        {"name": "a.htm", "type": "text.gif", "size": "1"},
                        {"name": "b.htm", "type": "text.gif", "size": "1"},
                    ]
                }
            }
            assert _filenames_from_sec_index_json(raw) == ["a.htm", "b.htm"]

    class TestVerifyAndParseEdgarSubmissionsRecentFilings:
        """_verify_and_parse_edgar_submissions_recent_filings"""

        base_raw = {
            "accessionNumber": ["0000320193-23-000106"],
            "filingDate": ["2026-04-05"],
            "reportDate": ["2026-04-05"],
            "acceptanceDateTime": ["2026-04-05T12:00:00.000Z"],
            "act": ["10-K"],
            "form": ["10-K"],
            "items": ["10-K"],
            "core_type": ["10-K"],
            "isXBRL": [True],
            "isInlineXBRL": [False],
            "primaryDocument": ["10-K"],
            "primaryDocDescription": ["10-K"],
        }

        def test_verify_and_parse_edgar_submissions_recent_filings_success(
            self,
        ) -> None:
            """verify_and_parse_edgar_submissions_recent_filings が正常に動作する"""
            assert _verify_and_parse_edgar_submissions_recent_filings(
                cik="0000320193", recent=self.base_raw
            ) == {
                "accessionNumber": ["0000320193-23-000106"],
                "filingDate": ["2026-04-05"],
                "reportDate": ["2026-04-05"],
                "acceptanceDateTime": ["2026-04-05T12:00:00.000Z"],
                "act": ["10-K"],
                "form": ["10-K"],
                "items": ["10-K"],
                "core_type": ["10-K"],
                "isXBRL": [True],
                "isInlineXBRL": [False],
                "primaryDocument": ["10-K"],
                "primaryDocDescription": ["10-K"],
            }

        def test_verify_and_parse_edgar_submissions_recent_filings_missing_property(
            self,
        ) -> None:
            """verify_and_parse_edgar_submissions_recent_filings がプロパティが不足しているとエラーを返す"""
            raw = self.base_raw.copy()
            del raw["primaryDocument"]
            with pytest.raises(CollectorParseResponseValidationError):
                _verify_and_parse_edgar_submissions_recent_filings(
                    cik="0000320193", recent=raw
                )

        def test_verify_and_parse_edgar_submissions_recent_filings_length_mismatch(
            self,
        ) -> None:
            """verify_and_parse_edgar_submissions_recent_filings が長さが一致しないとエラーを返す"""
            raw = self.base_raw.copy()
            raw["accessionNumber"] = ["0000320193-23-000106", "0000320193-23-000107"]
            with pytest.raises(CollectorParseResponseValidationError):
                _verify_and_parse_edgar_submissions_recent_filings(
                    cik="0000320193", recent=raw
                )
