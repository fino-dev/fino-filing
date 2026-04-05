import pytest

from fino_filing.collector.edgar._helper import (
    _build_recent_submissions_json_file_name,
    _filenames_from_sec_index_json,
    _format_from_primary_filename,
)


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edgar
class TestEdgarHelpers:
    class TestBuildRecentSubmissionsJsonFileName:
        def test_10_cik(self) -> None:
            """ """
            assert (
                _build_recent_submissions_json_file_name("1234567890")
                == "CIK1234567890-submissions.json"
            )

        def test_empty_cik(self) -> None:
            """ """
            assert (
                _build_recent_submissions_json_file_name("")
                == "CIK0000000000-submissions.json"
            )

    class TestBuildCompanyFactsJsonFileName:
        def test_10_cik(self) -> None:
            """ """
            assert (
                _build_company_facts_json_file_name("1234567890")
                == "CIK1234567890-companyfacts.json"
            )

        def test_empty_cik(self) -> None:
            """ """
            assert (
                _build_company_facts_json_file_name("")
                == "CIK0000000000-companyfacts.json"
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

        def test_filenames_from_sec_index_htm_extracts_archive_hrefs(self) -> None:
            """index.htm から Archives 配下の文書パスを重複なく抽出する"""
            html = (
                b'<a href="/Archives/edgar/data/320193/000032019325000057/a.htm">a</a>'
                b'<a href="/ix?doc=/Archives/edgar/data/320193/000032019325000057/b.xml">b</a>'
            )
            assert _filenames_from_sec_index_htm(html) == ["a.htm", "b.xml"]

    class TestFormatAndZip:
        def test_format_from_primary_filename_nested_path(self) -> None:
            """相対パスにサブディレクトリがあっても拡張子を推定する"""
            assert _format_from_primary_filename("xslF345X05/wk-form4_1.xml") == "xml"

        def test_filing_entries_zip_bytes_roundtrip(self) -> None:
            """複数エントリを ZIP にまとめられる"""
            z = _filing_entries_zip_bytes({"a.txt": b"hi", "d/b.bin": b"\x00"})
            assert isinstance(z, bytes)
            assert len(z) > 20
