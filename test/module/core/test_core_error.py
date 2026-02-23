import pytest

from fino_filing.core.error import FinoFilingException


class TestFinoFilingException:
    """FinoFilingExceptionのテスト"""

    def test_fino_filing_exception_message(self) -> None:
        with pytest.raises(FinoFilingException) as e:
            raise FinoFilingException("test message")
        assert e.value.message == "[Fino Filing] test message"
