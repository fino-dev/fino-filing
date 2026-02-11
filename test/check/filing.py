from datetime import datetime

from fino_filing import Filing
from fino_filing.filing.filing import EDINETFiling

filing = Filing(
    id="hoge_id",
    source="test",
    checksum="123",
    name="test.zip",
    is_zip=True,
    created_at=datetime.now(),
)

print("<<< class >>>")
print(Filing)
print("<<< instance >>>")
print(filing)
print("<<< instance __class__ >>>")
print(filing.__class__)
print("<<< instance __class__.__bases__ >>>")
print(filing.__class__.__bases__)
print("<<< instance __class__._fields >>>")
print(getattr(filing.__class__, "_fields", {}))
print("<<< instance __class__._defaults >>>")
print(getattr(filing.__class__, "_defaults", {}))

edinet_filing = EDINETFiling(
    id="edinet_id",
    checksum="123",
    name="test.zip",
    is_zip=True,
    created_at=datetime.now(),
    edinet_code="hoge",
    sec_code="hoge",
    jcn="hoge",
    filer_name="hoge",
    ordinance_code="hoge",
    form_code="hoge",
    doc_description="hoge",
    period_start=datetime.now(),
    period_end=datetime.now(),
    submit_datetime=datetime.now(),
)

print("<<< edinet class >>>")
print(EDINETFiling)
print("<<< edinet instance >>>")
print(edinet_filing)
print("<<< edinet instance __class__ >>>")
print(edinet_filing.__class__)
print("<<< edinet instance __class__.__bases__ >>>")
print(edinet_filing.__class__.__bases__)
print("<<< edinet instance __class__._fields >>>")
print(getattr(edinet_filing.__class__, "_fields", {}))
print("<<< edinet instance __class__._defaults >>>")
print(getattr(edinet_filing.__class__, "_defaults", {}))
