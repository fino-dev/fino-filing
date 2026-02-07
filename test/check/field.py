import datetime

from fino_filing import Filing

filing = Filing(
    id="123",
    source="test",
    checksum="123",
    name="test.zip",
    is_zip=True,
    created_at=datetime.now(),
)

print(filing)
