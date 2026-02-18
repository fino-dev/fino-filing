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
            created_at=datetime(2024, 1, 15),
        )
        path = locator.resolve(filing)
        assert path is not None
        assert isinstance(path, str)
        assert path == "test/test:001:abc12345"

    def test_resolve_with_enpty_values(self) -> None:
        """空の値でresolve成功"""
        locator = Locator()
        filing = Filing(
            id="",
            source="",
            checksum="",
            name="",
            is_zip=False,
            created_at=datetime(2024, 1, 15),
        )

        path = locator.resolve(filing)
        assert path is not None
        assert isinstance(path, str)
        assert path == "/"  # TODO これはまずい、そもそもIDをうわけ渡すのがよくなさそう
