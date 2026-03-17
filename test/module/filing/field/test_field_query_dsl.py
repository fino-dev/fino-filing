"""Field の Query DSL（Expr を返す演算・メソッド）のテスト。観点: 各メソッドが期待する Expr を返すこと。"""

import pytest

from fino_filing import Expr, Field


@pytest.mark.module
@pytest.mark.filing
class TestField_QueryDSL_Comparison:
    """比較演算子。indexed で sql が物理カラム / json_extract に分かれること。"""

    def test_eq_indexed_uses_column_name(self) -> None:
        f = Field("col", indexed=True)
        e = f == 1
        assert isinstance(e, Expr)
        assert e.sql == "col = ?"
        assert e.params == [1]

    def test_eq_not_indexed_uses_json_extract(self) -> None:
        f = Field("col", indexed=False)
        e = f == 1
        assert e.sql == "json_extract(data, '$.col') = ?"
        assert e.params == [1]

    def test_ne_gt_ge_lt_le_return_expr(self) -> None:
        f = Field("x")
        assert (f != 0).params == [0]
        assert "!=" in (f != 0).sql
        assert (f > 0).params == [0]
        assert ">" in (f > 0).sql
        assert (f >= 0).params == [0]
        assert (f < 0).params == [0]
        assert (f <= 0).params == [0]


@pytest.mark.module
@pytest.mark.filing
class TestField_QueryDSL_String:
    """contains / startswith / endswith。LIKE と % 付き params。"""

    def test_contains_returns_expr_with_like_and_wildcards(self) -> None:
        e = Field("name").contains("x")
        assert isinstance(e, Expr)
        assert "LIKE" in e.sql
        assert e.params == ["%x%"]

    def test_startswith_returns_expr(self) -> None:
        e = Field("name").startswith("a")
        assert "LIKE" in e.sql
        assert e.params == ["a%"]

    def test_endswith_returns_expr(self) -> None:
        e = Field("name").endswith("z")
        assert "LIKE" in e.sql
        assert e.params == ["%z"]


@pytest.mark.module
@pytest.mark.filing
class TestField_QueryDSL_Set:
    """in_ / not_in。IN (?,?) と params にリスト。"""

    def test_in_returns_expr(self) -> None:
        e = Field("src").in_(["A", "B"])
        assert isinstance(e, Expr)
        assert "IN (?, ?)" in e.sql
        assert e.params == ["A", "B"]

    def test_not_in_returns_expr(self) -> None:
        e = Field("src").not_in([1, 2])
        assert "NOT IN (?, ?)" in e.sql
        assert e.params == [1, 2]


@pytest.mark.module
@pytest.mark.filing
class TestField_QueryDSL_Null:
    """is_null / is_not_null。params は空。"""

    def test_is_null_returns_expr_no_params(self) -> None:
        e = Field("opt").is_null()
        assert isinstance(e, Expr)
        assert "IS NULL" in e.sql
        assert e.params == []

    def test_is_not_null_returns_expr_no_params(self) -> None:
        e = Field("opt").is_not_null()
        assert "IS NOT NULL" in e.sql
        assert e.params == []


@pytest.mark.module
@pytest.mark.filing
class TestField_QueryDSL_Range:
    """between。BETWEEN ? AND ? と [lower, upper]。"""

    def test_between_returns_expr(self) -> None:
        e = Field("n").between(1, 10)
        assert isinstance(e, Expr)
        assert "BETWEEN ? AND ?" in e.sql
        assert e.params == [1, 10]
