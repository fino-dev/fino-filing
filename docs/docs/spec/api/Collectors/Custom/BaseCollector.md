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

### collect

```python
collect() -> list[tuple[Filing, str]]
```

For each item from `fetch_documents()`: calls `parse_response(raw)` → `build_filing(parsed, raw)` → `add_to_collection(filing, raw.content)`. Returns the list of `(Filing, path)` returned by `add_to_collection`. If an error occurs mid-run, previously processed documents remain saved.

### add_to_collection

```python
add_to_collection(filing: Filing, content: bytes) -> tuple[Filing, str]
```

Delegates to `collection.add(filing, content)`. Same return and exceptions as [Collection.add](../Collection/Collection#add).

### Abstract methods (subclass must implement)

| Method                                           | Returns                 | Description                                               |
| ------------------------------------------------ | ----------------------- | --------------------------------------------------------- |
| `fetch_documents()`                              | `Iterator[RawDocument]` | Yield one RawDocument per fetched document                |
| `parse_response(raw: RawDocument)`               | `Parsed`                | Turn raw into a dict for build_filing                     |
| `build_filing(parsed: Parsed, raw: RawDocument)` | `Filing`                | Build Filing from parsed data and raw (e.g. for checksum) |
