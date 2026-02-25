from __future__ import annotations

import json
from datetime import datetime as dt
from typing import Any, Optional, Type

import duckdb

from fino_filing.filing.filing import Filing

from fino_filing.collection.error import CatalogRequiredValueError
from fino_filing.collection.filing_resolver import FilingResolver
from fino_filing.filing.expr import Expr


# 物理カラムとして常に存在するコアフィールド（INSERT 順序の先頭）
_CORE_COLUMNS = (
    "id",
    "source",
    "checksum",
    "name",
    "is_zip",
    "format",
    "created_at",
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

    def __init__(self, db_path: str, resolver: Optional[FilingResolver] = None) -> None:
        """
        Args:
            db_path: DuckDBファイルパス
            resolver: Filing 復元用の解決器。None のときは default_resolver を使用
        """
        from fino_filing.collection.filing_resolver import default_resolver

        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._resolver = resolver if resolver is not None else default_resolver
        self._init_schema()

    def _init_schema(self):
        """
        スキーマ初期化
        """
        # 基本テーブル作成
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS filings (
                id VARCHAR PRIMARY KEY,
                source VARCHAR NOT NULL,
                checksum VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                is_zip BOOLEAN NOT NULL,
                format VARCHAR NOT NULL,
                created_at TIMESTAMP NOT NULL,
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

        self.conn.commit()

    def _get_table_column_names(self) -> list[str]:
        """filings テーブルのカラム名一覧を取得（data 除く物理カラム＋data）。"""
        result = self.conn.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'filings'
            ORDER BY ordinal_position
            """
        ).fetchall()
        return [row[0] for row in result] if result else []

    def _ensure_indexed_columns(self, filing_cls: Type[Filing]) -> None:
        """
        Filing クラスの indexed フィールドがテーブルに存在しない場合、ADD COLUMN とインデックスを作成する。
        """
        existing = set(self._get_table_column_names())
        indexed = filing_cls.get_indexed_fields()
        fields = getattr(filing_cls, "_fields", {})

        for name in indexed:
            if name in existing or name == "data":
                continue
            field = fields.get(name)
            py_type = getattr(field, "_field_type", None) if field else None
            duck_type = _py_type_to_duckdb(py_type) if py_type else "VARCHAR"
            self.conn.execute(
                f'ALTER TABLE filings ADD COLUMN "{name}" {duck_type}'
            )
            self.conn.execute(
                f'CREATE INDEX IF NOT EXISTS idx_{name} ON filings("{name}")'
            )
            existing.add(name)
        self.conn.commit()

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

        filing_json = json.dumps(filing_dict, ensure_ascii=False, default=str)
        columns = self._get_table_column_names()
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
        core_set: set[str] = {c for c in _CORE_COLUMNS if c != "data"}
        rows: list[list[Any]] = []

        for filing in filings:
            filing_dict = filing.to_dict()
            filing_dict["_filing_class"] = (
                f"{type(filing).__module__}.{type(filing).__qualname__}"
            )
            filing_json = json.dumps(filing_dict, ensure_ascii=False, default=str)
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

    def _resolve_data_to_filing(self, data: dict[str, Any]) -> Filing:
        """
        data から _filing_class を解決し Filing インスタンスを返す
        """

        data = dict(data)
        filing_cls_name = data.pop("_filing_class", None)
        cls = self._resolver.resolve(filing_cls_name) or Filing
        return cls.from_dict(data)

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

        Args:
            id: Filing ID

        Returns:
            data 辞書または None
        """
        result = self.conn.execute(
            """
            SELECT data FROM filings WHERE id = ?
        """,
            [id],
        ).fetchone()

        if not result:
            return None

        return json.loads(result[0])

    def search(
        self,
        expr: Expr | None = None,
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
        sql = "SELECT data FROM filings"
        params: list[Any] = []

        # WHERE句
        if expr:
            sql += f" WHERE {expr.sql}"
            params = expr.params

        # ORDER BY（物理カラムならそのまま、それ以外は json_extract）
        order_direction = "DESC" if desc else "ASC"
        table_columns = set(self._get_table_column_names())
        if order_by in table_columns and order_by != "data":
            sql += f" ORDER BY \"{order_by}\" {order_direction}"
        else:
            sql += f" ORDER BY json_extract(data, '$.{order_by}') {order_direction}"

        # LIMIT/OFFSET
        sql += f" LIMIT {limit} OFFSET {offset}"

        # 実行
        rows = self.conn.execute(sql, params).fetchall()
        raw_list = [json.loads(row[0]) for row in rows]
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

    def count(self, expr: Expr | None = None) -> int:
        """
        件数カウント

        Args:
            expr: 検索条件

        Returns:
            件数
        """
        sql = "SELECT COUNT(*) FROM filings"
        params = []

        if expr:
            sql += f" WHERE {expr.sql}"
            params = expr.params

        result = self.conn.execute(sql, params).fetchone()
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
