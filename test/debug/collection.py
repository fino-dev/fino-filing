from datetime import datetime
from pathlib import Path

from fino_filing import Collection, EDINETFiling

# プロジェクトルートからの相対パスでZIPを参照
_assets_dir = Path(__file__).resolve().parent.parent / "assets" / "edinet" / "xbrl"
_zip_path = _assets_dir / "annual_toyota_2023_06_30.zip"

collection = Collection()

edinet_filing = EDINETFiling(
    id="test_id",
    checksum="1562649a12b68d136e6a5fca40244a822e8b5907ad13ef715d2931c239929a99",
    name="test_name",
    is_zip=False,
    created_at=datetime.now(),
    edinet_code="test_edinet_code",
    sec_code="test_sec_code",
    jcn="test_jcn",
    filer_name="test_filer_name",
)

try:
    with open(_zip_path, "rb") as f:
        collection.add(edinet_filing, f.read())
except Exception as e:
    print(e)

file = collection.get(edinet_filing.id)
print(file)
