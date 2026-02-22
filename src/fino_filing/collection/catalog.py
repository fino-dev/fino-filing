from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

import duckdb

from fino_filing.collection.error import CatalogRequiredValueError
from fino_filing.collection.filing_resolver import FilingResolver
from fino_filing.filing.expr import Expr
from fino_filing.filing.filing import Filing


class Catalog:
    """
    Catalog (Collection Index Database <Repository>)

    責務:
    - Filing の索引（index / index_batch）と _filing_class の付与
    - 検索（get / search）と Filing 復元（FilingResolver によるクラス解決）

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

        物理カラムは Filing.get_indexed_fields() から自動決定
        """
        # 基本テーブル作成
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS filings (
                id VARCHAR PRIMARY KEY,
                source VARCHAR NOT NULL,
                checksum VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                is_zip BOOLEAN NOT NULL,
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
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_created_at ON filings(created_at)"
        )

        self.conn.commit()

    def index(self, filing: Filing) -> None:
        """
        Filing索引

        Args:
            filing: 索引するFiling
        """
        dict_filing = filing.to_dict()

        core_values: dict[str, Any] = {
            "id": dict_filing.get("id"),
            "source": dict_filing.get("source"),
            "checksum": dict_filing.get("checksum"),
            "name": dict_filing.get("name"),
            "is_zip": dict_filing.get("is_zip", False),
            "created_at": dict_filing.get("created_at"),
        }

        # Catalog で復元時にクラスを解決するため _filing_class を保存
        dict_filing["_filing_class"] = (
            f"{type(filing).__module__}.{type(filing).__qualname__}"
        )

        # 必須フィールド検証
        for key in [
            "id",
            "source",
            "checksum",
            "name",
            "is_zip",
            "created_at",
        ]:
            # filing自体のvalidationで検証された状態だが、ここでも保存前に検証を行った
            if core_values[key] is None or core_values[key] == "":
                raise CatalogRequiredValueError(
                    field=key, actual_value=core_values[key]
                )

        # datetime変換
        if isinstance(core_values["created_at"], str):
            core_values["created_at"] = datetime.fromisoformat(
                core_values["created_at"]
            )

        # JSON化
        json_data = json.dumps(dict_filing, ensure_ascii=False, default=str)

        # 挿入
        self.conn.execute(
            """
            INSERT OR REPLACE INTO filings 
            (id, source, checksum, name, is_zip, created_at, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            [
                core_values["id"],
                core_values["source"],
                core_values["checksum"],
                core_values["name"],
                core_values["is_zip"],
                core_values["created_at"],
                json_data,
            ],
        )

        self.conn.commit()

    def index_batch(self, filings: list[Filing]):
        """
        バッチ索引

        Args:
            filings: Filing一覧
        """
        rows: list[list[Any]] = []

        for filing in filings:
            data = filing.to_dict()
            data["_filing_class"] = (
                f"{type(filing).__module__}.{type(filing).__qualname__}"
            )

            core_values: dict[str, Any] = {
                "id": data.get("id"),
                "source": data.get("source"),
                "checksum": data.get("checksum"),
                "name": data.get("name"),
                "is_zip": data.get("is_zip", False),
                "created_at": data.get("created_at"),
            }

            if isinstance(core_values["created_at"], str):
                core_values["created_at"] = datetime.fromisoformat(
                    core_values["created_at"]
                )

            json_data = json.dumps(data, ensure_ascii=False, default=str)

            rows.append(
                [
                    core_values["id"],
                    core_values["source"],
                    core_values["checksum"],
                    core_values["name"],
                    core_values["is_zip"],
                    core_values["created_at"],
                    json_data,
                ]
            )

        self.conn.executemany(
            """
            INSERT OR REPLACE INTO filings 
            (id, source, checksum, name, is_zip, created_at, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            rows,
        )

        self.conn.commit()

    def _resolve_data_to_filing(self, data: dict[str, Any]) -> Filing:
        """data から _filing_class を解決し Filing インスタンスを返す"""
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

        # ORDER BY
        order_direction = "DESC" if desc else "ASC"

        # 物理カラムか判定
        physical_columns = {
            "id",
            "source",
            "checksum",
            "name",
            "is_zip",
            "created_at",
        }

        if order_by in physical_columns:
            sql += f" ORDER BY {order_by} {order_direction}"
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
