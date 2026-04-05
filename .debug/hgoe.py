from datetime import datetime

from fino_filing import Collection, EDINETFiling

collection = Collection()

filing = EDINETFiling(
    id="test_id",
    checksum="6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72",
    name="test_name",
    is_zip=False,
    format="txt",
    created_at=datetime.now(),
    doc_id="test_doc_id",
    edinet_code="test_edinet_code",
    sec_code="test_sec_code",
    jcn="test_jcn",
    filer_name="test_filer_name",
)

print(filing)
print("----------------------------------------------------------------")

saved, path = collection.add(filing, b"test content")
print(path)
print("----------------------------------------------------------------")

get, content, path = collection.get(filing.id)
print(get)
print(content)
print(path)
print("----------------------------------------------------------------")

saved_filing = collection.get_filing(filing.id)
print(saved_filing)
print("----------------------------------------------------------------")

saved_content = collection.get_content(filing.id)
print(saved_content)
print("----------------------------------------------------------------")

saved_path = collection.get_path(filing.id)
print(saved_path)
print("----------------------------------------------------------------")
