import json
from datetime import datetime
from typing import Any

import duckdb

from fino_filing.filing.expr import Expr
from fino_filing.filing.filing import Filing


class Catalog:
    """
    Catalog (Collection Index Database <Repository>)

    Methods:
    - index: Add Filing to the catalog
    - index_batch: Add multiple Filing to the catalog
    - get: Get Filing from the catalog by ID
    - search: Search Filing from the catalog
    - search_raw: Search Filing from the catalog using raw SQL
    - count: Count the number of Filing in the catalog
    - stats: Get statistics of the catalog
    - clear: Clear the catalog
    - close: Close the catalog
    """

    def __init__(self, db_path: str):
        """
        Args:
            db_path: DuckDBファイルパス
        """
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
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

    def index(self, filing: Filing):
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
            if core_values[key] is None:
                raise ValueError(f"Required field '{key}' is missing")

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
        rows = []

        for filing in filings:
            data = filing.to_dict()

            core_values = {
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            rows,
        )

        self.conn.commit()

    def get(self, id_: str) -> dict | None:
        """
        ID指定取得

        Args:
            id_: Filing ID

        Returns:
            Filing辞書 or None
        """
        result = self.conn.execute(
            """
            SELECT data FROM filings WHERE id = ?
        """,
            [id_],
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
    ) -> list[dict]:
        """
        検索（Expression API）

        Args:
            expr: 検索条件（Exprオブジェクト）
            limit: 取得件数上限
            offset: オフセット
            order_by: ソートフィールド
            desc: 降順フラグ

        Returns:
            Filing辞書リスト
        """
        sql = "SELECT data FROM filings"
        params = []

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

        return [json.loads(row[0]) for row in rows]

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

    def stats(self) -> dict:
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
            "total": result[0],
            "sources": result[1],
            "earliest": result[2],
            "latest": result[3],
        }

    def clear(self):
        """全削除"""
        self.conn.execute("DELETE FROM filings")
        self.conn.commit()

    def close(self):
        """接続クローズ"""
        self.conn.close()
