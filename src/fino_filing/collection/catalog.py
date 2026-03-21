from __future__ import annotations

import json
from datetime import datetime as dt
from typing import Any, Optional, Type

import duckdb

from fino_filing.collection.error import CatalogExprTypeError, CatalogRequiredValueError
from fino_filing.collection.filing_resolver import FilingResolver
from fino_filing.filing.expr import Expr
from fino_filing.filing.filing import Filing

# 物理カラムとして常に存在するコアフィールド（INSERT 順序の先頭）
_CORE_COLUMNS = (
    "id",
    "source",
    "checksum",
    "name",
    "is_zip",
    "format",
    "created_at",
    "_filing_class",
    "data",
)


def _py_type_to_duckdb(py_type: Type[Any] | None) -> str:
    """Python 型を DuckDB のカラム型に変換する。"""
    if py_type is None:
        return "VARCHAR"
    if issubclass(py_type, str):
        return "VARCHAR"
    if issubclass(py_type, bool):
        return "BOOLEAN"
    if issubclass(py_type, dt):
        return "TIMESTAMP"
    if issubclass(py_type, int):
        return "BIGINT"
    if issubclass(py_type, float):
        return "DOUBLE"
    return "VARCHAR"


class Catalog:
    """
    Catalog (Collection Index Database <Repository>)

    責務:
    - Filing の索引（index / index_batch）と _filing_class の付与
    - 検索（get / search）と Filing 復元（FilingResolver によるクラス解決）
    - indexed なフィールドは動的に物理カラムとして追加する（スキーマ拡張）

    Methods:
    - index: Add Filing to the catalog
    - index_batch: Add multiple Filing to the catalog
    - get: Get Filing from the catalog by ID
    - get_raw: Get raw dict from the catalog by ID
    - search: Search Filing from the catalog
    - search_raw: Execute raw SQL (advanced)
    - count: Count the number of Filing in the catalog
    - stats: Get statistics of the catalog
    - clear: Clear the catalog
    - close: Close the catalog
    """

    def __init__(
        self, db_file_path: str, resolver: Optional[FilingResolver] = None
    ) -> None:
        """
        Args:
            db_file_path: DuckDBファイルパス
            resolver: Filing 復元用の解決器。None のときは default_resolver を使用
        """
        from fino_filing.collection.filing_resolver import default_resolver

        self.db_file_path = db_file_path
        self.conn = duckdb.connect(db_file_path)
        self._resolver = resolver if resolver is not None else default_resolver
        self._init_schema()

    def _init_schema(self):
        """
        スキーマ初期化
        """
        # 基本テーブル作成（_filing_class は復元時の具象クラス解決用の物理カラム）
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS filings (
                id VARCHAR PRIMARY KEY,
                source VARCHAR NOT NULL,
                checksum VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                is_zip BOOLEAN NOT NULL,
                format VARCHAR NOT NULL,
                created_at TIMESTAMP NOT NULL,
                _filing_class VARCHAR,
                data JSON NOT NULL
            )
        """)

        # インデックス作成
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_id ON filings(id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON filings(source)")
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_checksum ON filings(checksum)"
        )
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON filings(name)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_is_zip ON filings(is_zip)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_foramt ON filings(format)")
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_created_at ON filings(created_at)"
        )
        self.conn.execute(
            'CREATE INDEX IF NOT EXISTS idx_filing_class ON filings("_filing_class")'
        )

        self.conn.commit()

    def _get_table_column_names(self) -> list[str]:
        """
        filings テーブルのカラム名一覧を取得
        （物理カラム＋data）。
        """
        result = self.conn.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'filings'
            ORDER BY ordinal_position
            """
        ).fetchall()
        return [row[0] for row in result] if result else []

    def _ensure_indexed_columns(
        self,
        filing_cls: Type[
            Filing
        ],  # filing_clsはFilingのインスタンスではなく、Filingのクラス
    ) -> None:
        """
        Filing クラスの indexed が有効なフィールドがテーブルに物理カラムとして存在しない場合、物理カラムとインデックスを作成する
        """
        existing = set[str](self._get_table_column_names())
        indexed_fields = filing_cls.get_indexed_fields()
        fields = getattr(filing_cls, "_fields", {})

        for name in indexed_fields:
            if name in existing:
                continue
            field = fields.get(name)
            py_type = getattr(field, "_field_type", None) if field else None
            duck_type = _py_type_to_duckdb(py_type) if py_type else "VARCHAR"
            self.conn.execute(f'ALTER TABLE filings ADD COLUMN "{name}" {duck_type}')
            self.conn.execute(
                f'CREATE INDEX IF NOT EXISTS idx_{name} ON filings("{name}")'
            )
            existing.add(name)
        self.conn.commit()

    def _data_only_dict(
        self,
        filing_dict: dict[str, Any],
        indexed_columns: set[
            str
        ],  # indexed_columns は物理カラムの名前の集合。（dataカラムを除く）
    ) -> dict[str, Any]:
        """
        物理カラムを除いた辞書（dataカラムに保存するFieldのみ）を返す。
        """
        if "data" in indexed_columns:
            raise ValueError("dataカラムは物理カラムに含めることはできません")

        return {k: v for k, v in filing_dict.items() if k not in indexed_columns}

    def _row_to_full_doc(
        self, columns: list[str], row: tuple[Any, ...]
    ) -> dict[str, Any]:
        """
        1行（物理カラム）と data の JSON をマージして辞書を返す。（Filingの生成用）
        """

        # カラムの名前と値の辞書をzipしてdictを生成
        row_dict = dict[str, Any](zip(columns, row))

        # dataカラム内のJSONをロードして別dictに切り分ける
        data_str: Any = row_dict.pop("data", None)
        # data_str がJSON型かつprimitive型やnullでない場合にはdictに切り分ける。それ以外は空dictで定義する
        try:
            parsed_data: Any = json.loads(data_str) if data_str else {}
        except json.JSONDecodeError:
            parsed_data = {}

        # フラットなdictにマージする
        row_dict.update(parsed_data)

        return row_dict

    @staticmethod
    def _escape_sql_value(value: Any) -> str:
        """SQL のリテラルとして埋め込むために値をエスケープする。"""
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, dt):
            return "'" + value.isoformat().replace("'", "''") + "'"
        s = str(value).replace("'", "''")
        return f"'{s}'"

    @staticmethod
    def _expr_to_inline_sql(
        expr: Expr,
        indexed_columns: set[str] | None = None,
    ) -> str:
        """
        Expr のプレースホルダをエスケープしたリテラルで置換した SQL を返す。
        パラメータを execute に渡すと DuckDB が結果セットの JSON 変換に誤用することがあるため、
        WHERE 句はリテラル埋め込みにし、execute には空リストを渡す。
        indexed_columns を渡すと json_extract(data, '$.col') を "col" に書き換え、
        WHERE で data を参照しないようにする（DuckDB の JSON 解釈誤用を防ぐ）。
        """
        sql = expr.sql
        if indexed_columns:
            for col in indexed_columns:
                sql = sql.replace(f"json_extract(data, '$.{col}')", f'"{col}"')
        for value in expr.params:
            literal = Catalog._escape_sql_value(value)
            sql = sql.replace("?", literal, 1)
        return sql

    def _resolve_data_to_filing(self, data: dict[str, Any]) -> Filing:
        """
        data から _filing_class を解決し Filing インスタンスを返す
        変換後には_filing_class を属性から削除する
        """

        dict_data = dict(data)
        filing_cls_name = dict_data.pop("_filing_class", None)
        cls = self._resolver.resolve(filing_cls_name) or Filing

        return cls.from_dict(data=dict_data)

    def index(self, filing: Filing) -> None:
        """
        Filing索引

        indexed なフィールドは物理カラムとして保存する（不足カラムは動的に ADD COLUMN）。

        Args:
            filing: 索引するFiling
        """
        filing_dict = filing.to_dict()

        # Catalog で復元時にクラスを解決するため _filing_class を保存
        filing_dict["_filing_class"] = (
            f"{type(filing).__module__}.{type(filing).__qualname__}"
        )

        # コアフィールド（data 除く）の必須検証
        for key in _CORE_COLUMNS:
            if key == "data":
                continue
            value = filing_dict.get(key)
            if value is None or value == "":
                raise CatalogRequiredValueError(
                    field=key, actual_value=filing_dict.get(key)
                )

        # 不足している indexed カラムをテーブルに追加
        self._ensure_indexed_columns(type(filing))

        columns = self._get_table_column_names()
        indexed_columns = set(columns) - {"data"}
        data_only = self._data_only_dict(filing_dict, indexed_columns)
        filing_json = json.dumps(data_only, ensure_ascii=False, default=str)
        indexed_set = set(type(filing).get_indexed_fields())

        values: list[Any] = []
        for col in columns:
            if col == "data":
                values.append(filing_json)
            elif col in indexed_set or col in _CORE_COLUMNS:
                values.append(filing_dict.get(col))
            else:
                values.append(None)

        placeholders = ", ".join(["?"] * len(columns))
        cols_str = ", ".join(f'"{c}"' for c in columns)
        self.conn.execute(
            f"INSERT OR REPLACE INTO filings ({cols_str}) VALUES ({placeholders})",
            values,
        )
        self.conn.commit()

    def index_batch(self, filings: list[Filing]) -> None:
        """
        バッチ索引

        各 Filing の型ごとに indexed カラムを確保してから、同一のカラム順で一括 INSERT する。

        Args:
            filings: Filing一覧
        """
        for filing in filings:
            self._ensure_indexed_columns(type(filing))

        columns = self._get_table_column_names()
        indexed_columns = set(columns) - {"data"}
        core_set: set[str] = {c for c in _CORE_COLUMNS if c != "data"}
        rows: list[list[Any]] = []

        for filing in filings:
            filing_dict = filing.to_dict()
            filing_dict["_filing_class"] = (
                f"{type(filing).__module__}.{type(filing).__qualname__}"
            )
            data_only = self._data_only_dict(filing_dict, indexed_columns)
            filing_json = json.dumps(data_only, ensure_ascii=False, default=str)
            indexed_set = set(type(filing).get_indexed_fields())

            values: list[Any] = []
            for col in columns:
                if col == "data":
                    values.append(filing_json)
                elif col in indexed_set or col in core_set:
                    values.append(filing_dict.get(col))
                else:
                    values.append(None)
            rows.append(values)

        placeholders = ", ".join(["?"] * len(columns))
        cols_str = ", ".join(f'"{c}"' for c in columns)
        self.conn.executemany(
            f"INSERT OR REPLACE INTO filings ({cols_str}) VALUES ({placeholders})",
            rows,
        )
        self.conn.commit()

    def get(self, id: str) -> Filing | None:
        """
        ID指定取得（Filing として復元）

        Args:
            id: Filing ID

        Returns:
            Filing または None
        """
        raw = self.get_raw(id)
        if raw is None:
            return None
        return self._resolve_data_to_filing(raw)

    def get_raw(self, id: str) -> dict[str, Any] | None:
        """
        ID指定取得（生の辞書。Filing に復元しない）

        物理カラムと data カラム（追加フィールドのみの JSON）をマージした完全な辞書を返す。

        Args:
            id: Filing ID

        Returns:
            完全なフィールド辞書または None
        """
        columns = self._get_table_column_names()
        cols_str = ", ".join(f'"{c}"' for c in columns)
        row = self.conn.execute(
            f"SELECT {cols_str} FROM filings WHERE id = ?",
            [id],
        ).fetchone()

        if not row:
            return None

        return self._row_to_full_doc(columns, row)

    def search(
        self,
        expr: Expr | None | bool = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        desc: bool = True,
    ) -> list[Filing]:
        """
        検索（Expression API）。Filing として復元して返す。

        Args:
            expr: 検索条件（Exprオブジェクト）
            limit: 取得件数上限
            offset: オフセット
            order_by: ソートフィールド
            desc: 降順フラグ

        Returns:
            Filing リスト
        """
        if isinstance(expr, bool):
            raise CatalogExprTypeError(expr)

        columns = self._get_table_column_names()
        cols_str = ", ".join(f'"{c}"' for c in columns)
        sql = f"SELECT {cols_str} FROM filings"
        bind_params: list[Any] = []

        # WHERE句（パラメータを渡すと DuckDB が結果の JSON 変換に誤用するため、リテラル埋め込み）
        table_columns = set(columns)
        if expr:
            where_sql = Catalog._expr_to_inline_sql(
                expr, indexed_columns=table_columns - {"data"}
            )
            sql += f" WHERE {where_sql}"

        # ORDER BY（物理カラムならそのまま、それ以外は json_extract）
        order_direction = "DESC" if desc else "ASC"
        if order_by in table_columns and order_by != "data":
            sql += f' ORDER BY "{order_by}" {order_direction}'
        else:
            sql += f" ORDER BY json_extract(data, '$.{order_by}') {order_direction}"

        # LIMIT/OFFSET
        sql += f" LIMIT {limit} OFFSET {offset}"

        # 実行（物理カラム + data の追加フィールドをマージして復元）
        rows = self.conn.execute(sql, bind_params).fetchall()
        raw_list = [self._row_to_full_doc(columns, row) for row in rows]
        return [self._resolve_data_to_filing(d) for d in raw_list]

    def search_raw(self, sql: str, params: list[Any] | None = None) -> list[Any]:
        """
        SQL直接実行（高度なユーザー向け）

        Args:
            sql: SQL文
            params: パラメータ

        Returns:
            結果リスト
        """
        if params is None:
            params = []

        return self.conn.execute(sql, params).fetchall()

    def count(self, expr: Expr | None | bool = None) -> int:
        """
        件数カウント

        Args:
            expr: 検索条件

        Returns:
            件数
        """
        if isinstance(expr, bool):
            raise CatalogExprTypeError(expr)

        sql = "SELECT COUNT(*) FROM filings"
        bind_params: list[Any] = []

        if expr:
            columns = self._get_table_column_names()
            indexed_columns = set(columns) - {"data"}
            where_sql = Catalog._expr_to_inline_sql(
                expr, indexed_columns=indexed_columns
            )
            sql += f" WHERE {where_sql}"

        result = self.conn.execute(sql, bind_params).fetchone()
        return result[0] if result else 0

    def stats(self) -> dict[str, Any]:
        """
        統計情報

        Returns:
            統計辞書
        """
        result = self.conn.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT source) as sources,
                MIN(created_at) as earliest,
                MAX(created_at) as latest
            FROM filings
        """).fetchone()

        return {
            "total": result[0] if result else None,
            "sources": result[1] if result else None,
            "earliest": result[2] if result else None,
            "latest": result[3] if result else None,
        }

    def clear(self):
        """全削除"""
        self.conn.execute("DELETE FROM filings")
        self.conn.commit()

    def close(self):
        """接続クローズ"""
        self.conn.close()
