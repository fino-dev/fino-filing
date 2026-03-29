"""normalize_delimited_multivalue のテスト。"""

import pytest

from fino_filing.util.delimited_symbols import normalize_delimited_multivalue


@pytest.mark.module
class TestDelimitedSymbols_normalize_delimited_multivalue:
    """normalize_delimited_multivalue. 観点: 正規化キー生成"""

    def test_empty_and_none(self) -> None:
        """空入力は空文字列になる"""
        assert normalize_delimited_multivalue(None) == ""
        assert normalize_delimited_multivalue([]) == ""

    def test_sort_dedupe_strip(self) -> None:
        """重複除去・ソート・前後空白除去・パイプ区切り"""
        assert normalize_delimited_multivalue([" MSFT ", "AAPL", "AAPL"]) == "AAPL|MSFT"

    def test_single_token_wrapped(self) -> None:
        """1件でも両端にパイプが付く（部分一致誤検知防止）"""
        assert normalize_delimited_multivalue(["AAPL"]) == "AAPL"
