import sqlite3
from datetime import datetime
from typing import Any

from fino_filing.collection.models import CoreFiling


class IndexDB:
    """Index DB"""

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize_core_schema()
        self._field_cache = {}  # スキーマキャッシュ

    def _initialize_core_schema(self):
        """コアスキーマ初期化（固定部分）"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS filings (
                filing_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                checksum TEXT NOT NULL,
                submit_date TEXT NOT NULL,
                document_type TEXT,
                _path TEXT,
                _indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 動的フィールド格納用テーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS filing_fields (
                filing_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                field_value TEXT,
                field_type TEXT,
                PRIMARY KEY (filing_id, field_name),
                FOREIGN KEY (filing_id) REFERENCES filings(filing_id) ON DELETE CASCADE
            )
        """)

        # インデックス
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON filings(source)")
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_submit_date ON filings(submit_date)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_field_name ON filing_fields(field_name)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_field_value ON filing_fields(field_value)"
        )

        self.conn.commit()

    def index(self, filing: CoreFiling):
        """Filing索引（動的スキーマ対応）"""
        # 1. コアフィールド挿入
        self.conn.execute(
            """
            INSERT OR REPLACE INTO filings
            (filing_id, source, checksum, submit_date, document_type, _path)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                filing.filing_id,
                filing.source,
                filing.checksum,
                filing.submit_date.isoformat(),
                filing.document_type,
                filing._path,
            ),
        )

        # 2. 既存の動的フィールド削除
        self.conn.execute(
            "DELETE FROM filing_fields WHERE filing_id = ?", (filing.filing_id,)
        )

        # 3. 全フィールド挿入（Source固有 + カスタム）
        filing_dict = filing.to_dict()
        core_fields = {
            "filing_id",
            "source",
            "checksum",
            "submit_date",
            "document_type",
            "_path",
        }

        for field_name, field_value in filing_dict.items():
            if field_name in core_fields or field_name.startswith("_"):
                continue

            # 型推論
            field_type = self._infer_field_type(field_value)

            # 値を文字列化（検索用）
            if field_value is None:
                str_value = None
            elif isinstance(field_value, datetime):
                str_value = field_value.isoformat()
            else:
                str_value = str(field_value)

            self.conn.execute(
                """
                INSERT INTO filing_fields (filing_id, field_name, field_value, field_type)
                VALUES (?, ?, ?, ?)
            """,
                (filing.filing_id, field_name, str_value, field_type),
            )

        self.conn.commit()

    def _infer_field_type(self, value: Any) -> str:
        """型推論"""
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, datetime):
            return "DATE"
        else:
            return "TEXT"

    def search(self, **filters) -> list[dict]:
        """動的検索"""
        # Core fieldsのフィルタ
        core_conditions = []
        core_params = []

        # Dynamic fieldsのフィルタ
        dynamic_conditions = []
        dynamic_params = []

        core_fields = {"source", "submit_date", "document_type"}

        for key, value in filters.items():
            # 範囲検索対応
            if key.endswith("__gte"):
                field = key[:-5]
                if field in core_fields:
                    core_conditions.append(f"f.{field} >= ?")
                    core_params.append(value)
                else:
                    # 動的フィールドの範囲検索
                    dynamic_conditions.append(
                        "EXISTS (SELECT 1 FROM filing_fields ff WHERE ff.filing_id = f.filing_id AND ff.field_name = ? AND ff.field_value >= ?)"
                    )
                    dynamic_params.extend([field, str(value)])

            elif key.endswith("__lte"):
                field = key[:-5]
                if field in core_fields:
                    core_conditions.append(f"f.{field} <= ?")
                    core_params.append(value)
                else:
                    dynamic_conditions.append(
                        "EXISTS (SELECT 1 FROM filing_fields ff WHERE ff.filing_id = f.filing_id AND ff.field_name = ? AND ff.field_value <= ?)"
                    )
                    dynamic_params.extend([field, str(value)])

            elif key.endswith("__contains"):
                field = key[:-10]
                if field in core_fields:
                    core_conditions.append(f"f.{field} LIKE ?")
                    core_params.append(f"%{value}%")
                else:
                    dynamic_conditions.append(
                        "EXISTS (SELECT 1 FROM filing_fields ff WHERE ff.filing_id = f.filing_id AND ff.field_name = ? AND ff.field_value LIKE ?)"
                    )
                    dynamic_params.extend([field, f"%{value}%"])

            else:
                # 完全一致
                if key in core_fields:
                    core_conditions.append(f"f.{key} = ?")
                    core_params.append(value)
                else:
                    dynamic_conditions.append(
                        "EXISTS (SELECT 1 FROM filing_fields ff WHERE ff.filing_id = f.filing_id AND ff.field_name = ? AND ff.field_value = ?)"
                    )
                    dynamic_params.extend([key, str(value)])

        # WHERE句組み立て
        all_conditions = core_conditions + dynamic_conditions
        where_clause = " AND ".join(all_conditions) if all_conditions else "1=1"

        # クエリ実行
        query = f"""
            SELECT f.*, 
                   GROUP_CONCAT(ff.field_name || ':' || COALESCE(ff.field_value, 'NULL')) as dynamic_fields
            FROM filings f
            LEFT JOIN filing_fields ff ON f.filing_id = ff.filing_id
            WHERE {where_clause}
            GROUP BY f.filing_id
        """

        cursor = self.conn.execute(query, core_params + dynamic_params)

        results = []
        for row in cursor:
            data = dict(row)

            # 動的フィールドをパース
            if data["dynamic_fields"]:
                for field_pair in data["dynamic_fields"].split(","):
                    if ":" in field_pair:
                        name, value = field_pair.split(":", 1)
                        data[name] = None if value == "NULL" else value

            del data["dynamic_fields"]
            results.append(data)

        return results

    def get_schema(self, source: str = None) -> dict[str, str]:
        """スキーマ取得（実際に使用されているフィールド一覧）"""
        if source:
            cursor = self.conn.execute(
                """
                SELECT DISTINCT ff.field_name, ff.field_type
                FROM filing_fields ff
                JOIN filings f ON ff.filing_id = f.filing_id
                WHERE f.source = ?
            """,
                (source,),
            )
        else:
            cursor = self.conn.execute("""
                SELECT DISTINCT field_name, field_type
                FROM filing_fields
            """)

        schema = {
            # Core fields
            "filing_id": "TEXT",
            "source": "TEXT",
            "checksum": "TEXT",
            "submit_date": "DATE",
            "document_type": "TEXT",
        }

        # Dynamic fields
        for row in cursor:
            schema[row[0]] = row[1]

        return schema
