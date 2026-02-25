import pytest

from fino_filing.core.error import FinoFilingException


class TestFinoFilingException:
    """FinoFilingException. 観点: 異常系（基底例外の message 形式）"""

    def test_fino_filing_exception_message(self) -> None:
        """仕様: message は接頭辞 '[Fino Filing] ' を含む。検証: e.value.message"""
        with pytest.raises(FinoFilingException) as e:
            raise FinoFilingException("test message")
        assert e.value.message == "[Fino Filing] test message"
