import pytest
from fino_filing.util.edgar import pad_cik


@pytest.mark.module
@pytest.mark.util
@pytest.mark.edgar
class TestEdgarUtil:
    def test_pad_cik(self) -> None:
        assert pad_cik("1234567890") == "1234567890"
        assert pad_cik("123456789") == "0123456789"
        assert pad_cik("12345678") == "0012345678"
        assert pad_cik("1234567") == "0001234567"
        assert pad_cik("123456") == "0000123456"
        assert pad_cik("12345") == "0000012345"
        assert pad_cik("1234") == "0000001234"
        assert pad_cik("123") == "0000000123"
        assert pad_cik("12") == "0000000012"
        assert pad_cik("1") == "0000000001"
        assert pad_cik("") == "0000000000"
