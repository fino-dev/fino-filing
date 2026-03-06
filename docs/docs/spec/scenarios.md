# Usage Scenarios

## Basic usage

```python
from fino_filing import Collection, LocalStorage, Catalog

# Setup
storage = LocalStorage("./data")
catalog = Catalog("./index.db")
collection = Collection(storage=storage, catalog=catalog)

# Add a Filing (currently manual; EDINET API integration via Collector is planned)
from fino_filing import EDINETFiling

filing = EDINETFiling(source="edinet", name="doc.xbrl", checksum="...", format="xbrl", is_zip=False)
collection.add(filing, b"...")

# Search
from fino_filing import Expr, Field
filings = collection.search(expr=Field("source") == "edinet", limit=100, offset=0)

# Get metadata
filing = collection.get_filing("filing_id")
# Get file content (e.g. for arelle)
content = collection.get_content("filing_id")
# Or both
filing, content, path = collection.get("filing_id")
```

> Note: rebuild_index, verify_integrity, and migrate are not implemented yet. Collection (e.g. EdinetCollector) is planned.
