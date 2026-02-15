from typing import Any

from fino_filing.filing.error import FilingValidationError

from .expr import Expr


class Field:
    """
    フィールドDescriptor（Typed Query DSL）

    責務:
        - フィールドメタ情報保持
        - Query Expression生成
        - 型ヒント提供

    Collectionには依存しない。

    Usage:
        # スキーマレス検索（型は省略可能）
        Field("revenue") > 1_000_000
        Field("revenue", _field_type=int) > 1_000_000

        # モデルベース検索（FilingではAnnotatedの型からメタクラスが_field_typeを注入）
        EDINETFiling.filer_name == "Toyota"
    """

    def __init__(
        self,
        name: str = "",
        _field_type: type | None = None,
        indexed: bool = False,
        immutable: bool = False,
        description: str | None = None,
    ):
        """
        Args:
            name: Field Name
            _field_type: Field Type（省略可能。Filing定義時はAnnotatedの型から注入される）
            indexed: Index Flag
            immutable: Immutable Flag
            description: Description
        """
        self.name = name
        self._field_type: type | None = _field_type
        self.indexed = indexed
        self.immutable = immutable
        self.description = description

    def _create_expr(self, op: str, value: Any) -> Expr:
        """
        Expression生成（Collectionは知らない）

        Args:
            op: 演算子
            value: 比較値

        Returns:
            Expr
        """

        if self.indexed:
            sql = f"{self.name} {op} ?"
        else:
            sql = f"json_extract(data, '$.{self.name}') {op} ?"

        return Expr(sql, [value])

    # ========== 比較演算子 ==========
    def __eq__(self, value: Any) -> Expr:
        """等価: field == value"""
        return self._create_expr("=", value)

    def __ne__(self, value: Any) -> Expr:
        """不等価: field != value"""
        return self._create_expr("!=", value)

    def __gt__(self, value: Any) -> Expr:
        """より大きい: field > value"""
        return self._create_expr(">", value)

    def __ge__(self, value: Any) -> Expr:
        """以上: field >= value"""
        return self._create_expr(">=", value)

    def __lt__(self, value: Any) -> Expr:
        """より小さい: field < value"""
        return self._create_expr("<", value)

    def __le__(self, value: Any) -> Expr:
        """以下: field <= value"""
        return self._create_expr("<=", value)

    # ========== 文字列演算 ==========

    def contains(self, value: str) -> Expr:
        """部分一致: field LIKE '%value%'"""
        from .expr import Expr

        if self.indexed:
            sql = f"{self.name} LIKE ?"
        else:
            sql = f"json_extract(data, '$.{self.name}') LIKE ?"

        return Expr(sql, [f"%{value}%"])

    def startswith(self, value: str) -> Expr:
        """前方一致: field LIKE 'value%'"""
        from .expr import Expr

        if self.indexed:
            sql = f"{self.name} LIKE ?"
        else:
            sql = f"json_extract(data, '$.{self.name}') LIKE ?"

        return Expr(sql, [f"{value}%"])

    def endswith(self, value: str) -> Expr:
        """後方一致: field LIKE '%value'"""
        from .expr import Expr

        if self.indexed:
            sql = f"{self.name} LIKE ?"
        else:
            sql = f"json_extract(data, '$.{self.name}') LIKE ?"

        return Expr(sql, [f"%{value}"])

    # ========== 集合演算 ==========

    def in_(self, values: list[Any]) -> Expr:
        """IN句: field IN (v1, v2, ...)"""
        from .expr import Expr

        placeholders = ", ".join(["?"] * len(values))

        if self.indexed:
            sql = f"{self.name} IN ({placeholders})"
        else:
            sql = f"json_extract(data, '$.{self.name}') IN ({placeholders})"

        return Expr(sql, values)

    def not_in(self, values: list[Any]) -> Expr:
        """NOT IN句: field NOT IN (v1, v2, ...)"""
        from .expr import Expr

        placeholders = ", ".join(["?"] * len(values))

        if self.indexed:
            sql = f"{self.name} NOT IN ({placeholders})"
        else:
            sql = f"json_extract(data, '$.{self.name}') NOT IN ({placeholders})"

        return Expr(sql, values)

    # ========== NULL判定 ==========

    def is_null(self) -> Expr:
        """NULL判定: field IS NULL"""
        from .expr import Expr

        if self.indexed:
            sql = f"{self.name} IS NULL"
        else:
            sql = f"json_extract(data, '$.{self.name}') IS NULL"

        return Expr(sql, [])

    def is_not_null(self) -> Expr:
        """NOT NULL判定: field IS NOT NULL"""
        from .expr import Expr

        if self.indexed:
            sql = f"{self.name} IS NOT NULL"
        else:
            sql = f"json_extract(data, '$.{self.name}') IS NOT NULL"

        return Expr(sql, [])

    # ========== 範囲検索 ==========

    def between(self, lower: Any, upper: Any) -> Expr:
        """範囲検索: field BETWEEN lower AND upper"""
        from .expr import Expr

        if self.indexed:
            sql = f"{self.name} BETWEEN ? AND ?"
        else:
            sql = f"json_extract(data, '$.{self.name}') BETWEEN ? AND ?"

        return Expr(sql, [lower, upper])

    # ========== Descriptor Protocol ==========

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        """Descriptor protocol（モデルからのアクセス用）"""
        if obj is None:
            # クラスからのアクセス: EDINETFiling.filer_name
            return self
        else:
            # インスタンスからのアクセス: filing.filer_name
            # 1. instance._data に値があればそれを返す
            if self.name in obj._data:
                return obj._data[self.name]

            # 2. クラスのdefault値があればそれを返す
            if hasattr(objtype or type(obj), "_defaults"):
                defaults = getattr(objtype or type(obj), "_defaults")
                if self.name in defaults:
                    return defaults[self.name]

            # 3. どちらもなければNone
            return None

    def __set__(self, obj: Any, value: Any) -> None:
        """値の設定（immutableチェックはFiling側で実施）"""
        obj._data[self.name] = value

    def __repr__(self) -> str:
        return f"Field(name={self.name!r}, type={self._field_type}, indexed={self.indexed}, immutable={self.immutable})"


# ========== ショートカット関数 ==========


def F(name: str) -> Field:
    """
    スキーマレス検索用ショートカット

    Usage:
        F("revenue") > 1_000_000
    """
    return Field(name, indexed=False)
