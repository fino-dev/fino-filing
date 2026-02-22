from datetime import datetime

from fino_filing import Filing
from fino_filing.collection.locator import Locator


class TestLocator_Resolve:
    """
    Locatorのresolveメソッドをテストする。
    - 正常系: 正しいFilingでresolve成功
    """

    def test_resolve_success(self) -> None:
        """正常なFilingでresolve成功"""
        locator = Locator()
        filing = Filing(
            id="test:001:abc12345",
            source="test",
            checksum="1234567890",
            name="test.zip",
            is_zip=True,
            format="zip",
            created_at=datetime(2024, 1, 15),
        )
        path = locator.resolve(filing)
        assert path is not None
        assert isinstance(path, str)
        assert path == "test/test:001:abc12345.zip"

    def test_resolve_with_empty_values(self) -> None:
        """空の source/id のときはプレースホルダ _ を使い拡張子付きで返す"""
        locator = Locator()
        filing = Filing(
            id="",
            source="",
            checksum="",
            name="",
            is_zip=False,
            format="xbrl",
            created_at=datetime(2024, 1, 15),
        )

        path = locator.resolve(filing)
        assert path is not None
        assert isinstance(path, str)
        assert path == "_/_.xbrl"

    def test_resolve_uses_format_when_set_pdf(self) -> None:
        """format=pdf のときは .pdf 拡張子が付く"""
        locator = Locator()
        filing = Filing(
            id="doc:001",
            source="edinet",
            checksum="abc",
            name="report.pdf",
            is_zip=False,
            format="pdf",
            created_at=datetime(2024, 1, 15),
        )
        path = locator.resolve(filing)
        assert path == "edinet/doc:001.pdf"

    def test_resolve_uses_format_when_set_csv(self) -> None:
        """format=csv のときは .csv 拡張子が付く"""
        locator = Locator()
        filing = Filing(
            id="data:001",
            source="custom",
            checksum="def",
            name="data.csv",
            is_zip=False,
            format="csv",
            created_at=datetime(2024, 1, 15),
        )
        path = locator.resolve(filing)
        assert path == "custom/data:001.csv"

    def test_resolve_fallback_to_is_zip_when_format_empty(self) -> None:
        """format が空のときは is_zip で .zip または .xbrl にフォールバック"""
        locator = Locator()
        filing_zip = Filing(
            id="z:1",
            source="s",
            checksum="x",
            name="n",
            is_zip=True,
            format="",
            created_at=datetime(2024, 1, 15),
        )
        filing_xbrl = Filing(
            id="x:1",
            source="s",
            checksum="x",
            name="n",
            is_zip=False,
            format="",
            created_at=datetime(2024, 1, 15),
        )
        assert locator.resolve(filing_zip) == "s/z:1.zip"
        assert locator.resolve(filing_xbrl) == "s/x:1.xbrl"
