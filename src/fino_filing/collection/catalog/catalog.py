import json

import duckdb


class Catalog:
    def __init__(self, db_path: str):
        self.conn = duckdb.connect(db_path)
        self._init_scheme()

    def _init_scheme(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS filings (
            filing_id TEXT PRIMARY KEY,
            source TEXT NULL,
            checksum TEXT,
            filing_name TEXT,
            is_zip BOOLEAN,
            create_at TIMESTAMP,
            path TEXT,
            metadata JSON NULL
        )
        """)

        # よく検索するcoreだけindex
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_checksum ON filings(filing_id)"
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_create_at ON filings(create_at)"
        )

    def index(self, filing: Filing):
        data = filing.to_dict()

        core = {
            k: data.pop(k, None)
            for k in [
                "filing_id",
                "source",
                "checksum",
                "filing_name",
                "is_zip",
                "create_at",
                "path",
            ]
        }

        self.conn.execute(
            """
            INSERT OR REPLACE INTO filings
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            [
                core["filing_id"],
                core["source"],
                core["checksum"],
                core["filing_name"],
                core["is_zip"],
                core["create_at"],
                core["path"],
                json.dumps(data),
            ],
        )
