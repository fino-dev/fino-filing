# Quick Start

## Use case (current implementation)

```python
import fino_filing as fec

# Default: LocalStorage + Catalog under .fino/collection in the current directory
collection = fec.Collection()

# Or specify explicitly
storage = fec.LocalStorage("/path/to/data")
catalog = fec.Catalog("/path/to/index.db")
collection = fec.Collection(storage=storage, catalog=catalog)

# Add a Filing (e.g. EDINETFiling)
filing = fec.EDINETFiling(
    source="edinet",
    name="doc.xbrl",
    checksum="sha256hex...",
    format="xbrl",
    is_zip=False,
    # optional indexed fields
)
content = b"..."
collection.add(filing, content)

# Search (Expr API)
from fino_filing import Expr, Field
filings = collection.search(expr=Field("source") == "edinet", limit=100)

# Get by ID
filing = collection.get_filing("filing_id")
content = collection.get_content("filing_id")
# Or in one call
filing, content, path = collection.get("filing_id")
if filing:
    name = filing.name
# path is the relative storage path (str | None)
```

> Collection from the EDINET API (sync_catalog / collect) is planned.
