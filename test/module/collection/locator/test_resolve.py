from datetime import datetime

from fino_filing import Filing
from fino_filing.collection.locator import Locator


class TestLocator_Resolve:
    """
    Locatorのresolveメソッドをテストする。
    - 正常系: 正しいFilingでresolve成功
    - 正常系: zip化されているときは .zip 拡張子が付く
    """

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

    def test_resolve_success(self) -> None:
        """正常なFilingでresolve成功"""
        locator = Locator()
        filing = Filing(
            id="test:001:abc12345",
            source="test",
            checksum="1234567890",
            name="test.zip",
            is_zip=True,
            format="csv",
            created_at=datetime(2024, 1, 15),
        )
        path = locator.resolve(filing)
        assert path is not None
        assert isinstance(path, str)
        assert path == "test/test:001:abc12345.zip"
