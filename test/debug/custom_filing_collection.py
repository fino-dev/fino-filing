"""
カスタム Filing クラスを register_filing_class なしで保存・取得するデバッグスクリプト。

確認ポイント:
- add 時に _filing_class へ完全修飾名が記録されること
- get / find 時に動的インポートで保存時の型として復元されること
"""

import hashlib
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fino_filing import Collection, Field, Filing
from fino_filing.collection.catalog import Catalog
from fino_filing.collection.storage.flat_local import LocalStorage

logging.basicConfig(level=logging.DEBUG)

# ========== カスタム Filing 定義 ==========


class CustomFiling(Filing):
    """ユーザー定義の Filing サブクラス（register_filing_class は不要）"""

    report_type: Annotated[str, Field("report_type", description="レポート種別")] = ""
    fiscal_year: Annotated[int, Field("fiscal_year", description="会計年度")] = 0


# ========== セットアップ ==========

tmpdir = Path(tempfile.mkdtemp())
storage = LocalStorage(tmpdir)
catalog = Catalog(str(tmpdir / "index.db"))
collection = Collection(storage=storage, catalog=catalog)

content = b"sample filing content"
checksum = hashlib.sha256(content).hexdigest()

filing = CustomFiling(
    id="custom_001",
    source="user_defined",
    checksum=checksum,
    name="custom_report.pdf",
    is_zip=False,
    created_at=datetime.now(),
    report_type="annual",
    fiscal_year=2024,
)

# ========== add ==========

result_filing, path = collection.add(filing, content)
print(f"[add] path: {path}")
print(f"[add] type: {type(result_filing)}")

# ========== get (型の復元確認) ==========

fetched_filing, fetched_content = collection.get("custom_001")
print(f"\n[get] type: {type(fetched_filing)}")
print(f"[get] is CustomFiling: {type(fetched_filing) is CustomFiling}")
print(f"[get] report_type: {fetched_filing.report_type if fetched_filing else None}")
print(f"[get] fiscal_year: {fetched_filing.fiscal_year if fetched_filing else None}")
print(f"[get] content matches: {fetched_content == content}")

# ========== find (型の復元確認) ==========

results = collection.find()
print(f"\n[find] count: {len(results)}")
first = results[0] if results else None
print(f"[find] type: {type(first)}")
print(f"[find] is CustomFiling: {type(first) is CustomFiling}")
print(f"[find] report_type: {first.report_type if first else None}")
