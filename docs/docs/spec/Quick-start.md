---
sidebar_position: 1
---

# Quick Start

This guide walks you through **install** → **fetching documents from EDGAR and saving them locally** → **searching and retrieving** saved documents.

---

## 1. Installation

**Requirements**: Python 3.13+

From the repository root, run:

```bash
pip install .
```

For development, an editable install is convenient:

```bash
pip install -e .
# or
uv pip install -e .
```

:::tip About SEC EDGAR
The EDGAR API **requires a User-Agent header**. This library ships a default in `EdgerConfig`. Override if needed with `EdgerConfig(user_agent="YourApp contact@example.com")`.
:::

---

## 2. Set up a collection

You need a place to store documents (storage) and an index (catalog). The simplest option is the default `Collection()`, which uses `.fino/collection` in the current directory for both data and index.

```python
from fino_filing import Collection

# Default: saves under .fino/collection
collection = Collection()
```

To choose the paths explicitly, pass `LocalStorage` and `Catalog`:

```python
from fino_filing import Collection, LocalStorage, Catalog

storage = LocalStorage("/path/to/data")
catalog = Catalog("/path/to/index.db")
collection = Collection(storage=storage, catalog=catalog)
```

---

## 3. Fetch documents from EDGAR and save

Use `EdgerCollector` to pull filings from the SEC EDGAR Company Submissions API and add them to your `Collection`. Companies are identified by **CIK** (Central Index Key); e.g. Apple is `320193`.

```python
from fino_filing import (
    Collection,
    EdgerBulkData,
    EdgerCollector,
    EdgerConfig,
    EdgerSecApi,
)

collection = Collection()

config = EdgerConfig()
collector = EdgerCollector(
    collection,
    EdgerSecApi(config),
    EdgerBulkData(config),
    cik_list=["320193"],  # Apple's CIK
)

# Fetch and save (you can limit per company: limit_per_company=5, etc.)
collected = collector.collect()

# Each item is (Filing, relative storage path)
for filing, path in collected:
    print(filing.name, path)
```

`collect()` processes one document at a time (**fetch → parse → build_filing → add_to_collection**), so any documents processed before a failure are already saved.

---

## 4. Search and retrieve saved documents

### Search (Expr API)

```python
from fino_filing import Expr, Field

# e.g. up to 100 filings from EDGAR
filings = collection.search(
    expr=Field("source") == "EDGAR",
    limit=100,
)
```

### Get a single document

```python
# Metadata only by ID
filing = collection.get_filing("filing_id")

# Raw content (bytes) only
content = collection.get_content("filing_id")

# Metadata, content, and storage path together
filing, content, path = collection.get("filing_id")
if filing:
    print(filing.name, filing.form_type)
```

---

## Next steps

- **Use cases**: See [Scenarios](/docs/spec/Usecase/scenarios) for typical workflows.
- **API contract**: Exceptions and return values are described in the [API spec](/docs/spec/intro).
- **EDINET**: For Japanese filings, use `EDINETFiling` and `collection.add()` manually. An EDINET API Collector is planned.
