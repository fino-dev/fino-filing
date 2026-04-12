---
slug: Storage
---
# Storage

Protocol for saving and loading filing content by path. Collection uses it for raw bytes; path resolution is done by Locator.

## Protocol

```python
class Storage(Protocol):
    base_dir: Path

    def save(
        self,
        content: bytes,
        storage_key: str | None = None,
    ) -> str:
        ...
    # Returns: path where content was saved (absolute path as str)

    def load_by_path(self, relative_path: str) -> bytes:
        ...

    def delete(self, relative_path: str) -> None:
        ...
```

- **save**: Persists `content` at the path derived from `storage_key` (relative). Caller (Collection + Locator) is responsible for providing a valid `storage_key`. Returns the absolute path of the saved file.
- **load_by_path**: Loads bytes for the given relative path. Resolution from filing id to path is the caller’s responsibility.
- **delete**: Removes the file at `relative_path` if it exists; implementations should not raise for missing paths or invalid keys (see `LocalStorage`).

Built-in implementation: [LocalStorage](/docs/spec/api/Collections/Storage/LocalStorage).
