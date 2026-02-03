import sqlite3


class IndexDB:
    """Index DB（キャッシュ層）"""

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self):
        """スキーマ初期化"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS filings (
                filing_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                checksum TEXT NOT NULL,
                document_type TEXT,
                submit_date TEXT,
                company_name TEXT,
                _path TEXT,
                _indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON filings(source)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON filings(submit_date)")
        self.conn.commit()

    def index(self, filing):
        """Filing索引"""
        self.conn.execute(
            """
            INSERT OR REPLACE INTO filings
            (filing_id, source, source_id, checksum, document_type, 
             submit_date, company_name, _path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                filing.filing_id,
                filing.source,
                filing.source_id,
                filing.checksum,
                filing.document_type,
                filing.submit_date.isoformat(),
                filing.company_name,
                filing.metadata.get("_path"),
            ),
        )
        self.conn.commit()

    def search(self, **filters) -> list[dict]:
        """検索（高速）"""
        conditions = []
        params = []

        for key, value in filters.items():
            conditions.append(f"{key} = ?")
            params.append(value)

        where = " AND ".join(conditions) if conditions else "1=1"

        cursor = self.conn.execute(f"SELECT * FROM filings WHERE {where}", params)
        return [dict(row) for row in cursor]

    def get(self, filing_id: str) -> dict | None:
        """ID取得"""
        cursor = self.conn.execute(
            "SELECT * FROM filings WHERE filing_id = ?", (filing_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def clear(self):
        """全削除（再構築前）"""
        self.conn.execute("DELETE FROM filings")
        self.conn.commit()

    def rebuild(self, registry_mgr):
        """Registry から DB再構築"""
        self.clear()

        count = 0
        for registry in registry_mgr.scan_all():
            for memento in registry.filings:
                self.conn.execute(
                    """
                    INSERT INTO filings
                    (filing_id, source, source_id, checksum, document_type, submit_date, company_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        memento.filing_id,
                        memento.source,
                        memento.source_id,
                        memento.checksum,
                        memento.document_type,
                        memento.submit_date,
                        "",  # company_nameはregistryに含めない想定
                    ),
                )
                count += 1

        self.conn.commit()
        print(f"Rebuilt index with {count} filings")
