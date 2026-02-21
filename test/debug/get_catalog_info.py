"""
Catalog に保存されている情報を列挙して出力する debug 用スクリプト。

実行:
  uv run python test/debug/get_catalog_info.py
  またはプロジェクトルートで:
  uv run python -m test.debug.get_catalog_info

DuckDB で terminal から同様に確認する方法:
--------------------------------------------------------------------------------
  ※ duckdb CLI は Python パッケージに含まれない。別途インストールする場合:
     macOS:  brew install duckdb
     その他: https://duckdb.org/docs/installation/ を参照

  【方法A】duckdb CLI が入っている場合（対話モード）:
    duckdb .fino/collection/index.db

    対話セッション内の SQL 例:
      SHOW TABLES;
      DESCRIBE filings;
      SELECT COUNT(*) FROM filings;
      SELECT COUNT(*) AS total, COUNT(DISTINCT source) AS sources,
             MIN(created_at) AS earliest, MAX(created_at) AS latest FROM filings;
      SELECT id, source, name, created_at FROM filings ORDER BY created_at DESC;
      SELECT source, COUNT(*) AS cnt FROM filings GROUP BY source;
      SELECT id, json_pretty(data) FROM filings LIMIT 1;
      .quit

  【方法B】CLI なしで Python から対話的に確認（uv でそのまま使える）:
    uv run python

    >>> import duckdb
    >>> conn = duckdb.connect(".fino/collection/index.db")
    >>> conn.execute("SELECT COUNT(*) FROM filings").fetchall()
    >>> conn.execute("SELECT id, source, name, created_at FROM filings ORDER BY created_at DESC").fetchall()
    >>> conn.execute("SELECT source, COUNT(*) AS cnt FROM filings GROUP BY source").fetchall()
    >>> conn.close()
--------------------------------------------------------------------------------
"""

import logging
import sys
from pathlib import Path
from typing import Any, cast

# プロジェクトルートを path に追加
root = Path(__file__).resolve().parents[2]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from fino_filing import Catalog  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    default_path = Path.cwd() / ".fino" / "collection" / "index.db"
    db_path = default_path

    if not db_path.exists():
        logger.info("Catalog not found: %s", db_path)
        logger.info("Create a collection first (e.g. add filings).")
        return

    catalog = Catalog(str(db_path))
    try:
        total = catalog.count()
        logger.info("=== Catalog: %s ===", db_path)
        logger.info("Total filings: %d", total)

        if total == 0:
            catalog.close()
            return

        st = cast(dict[str, Any], catalog.stats())  # type: ignore[reportUnknownMemberType]
        logger.info(
            "Stats: sources=%s, earliest=%s, latest=%s",
            st["sources"],
            st["earliest"],
            st["latest"],
        )

        # 全件を search で取得（data は Filing の to_dict() の JSON）
        rows = catalog.search(limit=total)
        logger.info("--- Listing filings (id, source, name, created_at) ---")
        for i, data in enumerate(rows, start=1):
            fid = data.get("id", "?")
            source = data.get("source", "?")
            name = data.get("name", "?")
            created = data.get("created_at", "?")
            logger.info("%d. id=%s source=%s name=%s created_at=%s", i, fid, source, name, created)

        logger.info("--- End of list ---")
    finally:
        catalog.close()


if __name__ == "__main__":
    main()
