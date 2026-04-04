---
sidebar_position: 1
title: LocalStorage
---

# LocalStorage

Storage implementation that writes and reads files under a single base directory. Path resolution (Filing → path) is done by the caller (Locator); `storage_key` must be a relative path.

## Constructor

```python
LocalStorage(base_dir: str | Path) -> LocalStorage
```

- **base_dir**: Directory for all files. Created if missing (`mkdir(parents=True, exist_ok=True)`).

## Methods

### save

```python
save(content: bytes, storage_key: str | None = None) -> str
```

- **storage_key**: Required. Relative path (e.g. `Edgar/abc123/index.htm`). Must not be absolute, empty, or contain `..`. Parent directories are created as needed.
- **Returns**: Absolute path of the saved file.
- **Raises**: `ValueError` if `storage_key` is missing, absolute, or escapes `base_dir`.

### load_by_path

```python
load_by_path(relative_path: str) -> bytes
```

Reads the file at `base_dir / relative_path`. Raises if path is invalid or file not found.
