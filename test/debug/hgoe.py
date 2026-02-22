from datetime import datetime

from fino_filing import Collection, EDINETFiling

collection = Collection()

filing = EDINETFiling(
    id="test_id",
    checksum="test_checksum",
    name="test_name",
    is_zip=True,
    format="zip",
    created_at=datetime.now(),
    doc_id="test_doc_id",
    edinet_code="test_edinet_code",
    sec_code="test_sec_code",
    jcn="test_jcn",
    filer_name="test_filer_name",
)

print(filing)
