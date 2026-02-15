from typing import Any


class Expr:
    """
    クエリ式（WHERE句の抽象表現）

    責務:
        - SQL WHERE句の表現
        - 論理演算（AND/OR/NOT）
        - パラメータ管理

    Collectionがこれをコンパイルする。
    """

    def __init__(self, sql: str, params: list[Any]):
        """
        Args:
            sql: SQL WHERE句（プレースホルダー含む）
            params: バインドパラメータ
        """
        self.sql = sql
        self.params = params

    def __and__(self, other: "Expr") -> "Expr":
        """
        AND結合

        Usage:
            (Field("a") == 1) & (Field("b!) == 2)
        """
        return Expr(f"{self.sql} AND {other.sql}", self.params + other.params)

    def __or__(self, other: "Expr") -> "Expr":
        """
        OR結合

        Usage:
            (Field("a") == 1) | (Field("b!) == 2)
        """
        return Expr(f"{self.sql} OR {other.sql}", self.params + other.params)

    def __invert__(self) -> "Expr":
        """
        NOT結合

        Usage:
            ~(Field("a") == 1)
        """
        return Expr(f"NOT ({self.sql})", self.params)

    def __repr__(self):
        return f"Expr(sql={self.sql}, params={self.params!r})"
