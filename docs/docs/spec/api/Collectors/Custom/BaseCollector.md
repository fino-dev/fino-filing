---
sidebar_position: 0
---

# BaseCollector

Abstract base class for the collect flow. Subclasses implement `fetch_documents`, `parse_response`, and `build_filing`.

## Constructor

```python
BaseCollector(collection: Collection) -> BaseCollector
```

- **collection**: Collection to which filings and content are added.

## Methods

### iter_collect

```python
iter_collect(**criteria: Any) -> Iterator[tuple[Filing, str]]
```

For each item from `fetch_documents(**criteria)`: calls `parse_response(raw)` → `build_filing(parsed, raw)` → `add_to_collection(filing, raw.content)`, and **yields** each `(Filing, path)` from `add_to_collection`. Use this when the caller needs progress per item or may stop early. If iteration stops early, documents already yielded remain saved.

### collect

```python
collect(**criteria: Any) -> list[tuple[Filing, str]]
```

Equivalent to `list(iter_collect(**criteria))`. If an error occurs mid-run, previously processed documents remain saved.

### add_to_collection

```python
add_to_collection(filing: Filing, content: bytes) -> tuple[Filing, str]
```

Delegates to `collection.add(filing, content)`. Same return and exceptions as [Collection.add](/docs/spec/api/Collections/Collection#add).

### Abstract methods (subclass must implement)

| Method                                           | Returns                 | Description                                               |
| ------------------------------------------------ | ----------------------- | --------------------------------------------------------- |
| `fetch_documents()`                              | `Iterator[RawDocument]` | Yield one RawDocument per fetched document                |
| `parse_response(raw: RawDocument)`               | `Parsed`                | Turn raw into a dict for build_filing                     |
| `build_filing(parsed: Parsed, raw: RawDocument)` | `Filing`                | Build Filing from parsed data and raw (e.g. for checksum) |
