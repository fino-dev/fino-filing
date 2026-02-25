"""Expr の単体テスト。観点: 正常系（AND/OR/NOT の結合と params）"""

from fino_filing import Expr


class TestExpr_Init:
    """Expr. 観点: 正常系（初期化）"""

    def test_expr_init(self) -> None:
        """sql と params を保持する"""
        e = Expr("id = ?", ["x"])
        assert e.sql == "id = ?"
        assert e.params == ["x"]


class TestExpr_And:
    """Expr.__and__. 観点: 正常系"""

    def test_and_combines_sql_and_params(self) -> None:
        """AND 結合で sql が AND でつながり、params が連結される"""
        a = Expr("id = ?", ["a"])
        b = Expr("source = ?", ["b"])
        c = a & b
        assert c.sql == "id = ? AND source = ?"
        assert c.params == ["a", "b"]


class TestExpr_Or:
    """Expr.__or__. 観点: 正常系"""

    def test_or_combines_sql_and_params(self) -> None:
        """OR 結合で sql が OR でつながり、params が連結される"""
        a = Expr("id = ?", ["a"])
        b = Expr("id = ?", ["b"])
        c = a | b
        assert c.sql == "id = ? OR id = ?"
        assert c.params == ["a", "b"]


class TestExpr_Invert:
    """Expr.__invert__. 観点: 正常系"""

    def test_invert_wraps_sql_in_not(self) -> None:
        """NOT で sql が NOT ( ... ) になり、params はそのまま"""
        a = Expr("id = ?", ["x"])
        c = ~a
        assert c.sql == "NOT (id = ?)"
        assert c.params == ["x"]
