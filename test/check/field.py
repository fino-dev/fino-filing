import datetime

from fino_filing import Filing

filing = Filing(
    id="hoge_id",
    source="test",
    checksum="123",
    name="test.zip",
    is_zip=True,
    created_at=datetime.time(),
)

print("class")
print(Filing.id)
print("instance")
print(filing.id)
