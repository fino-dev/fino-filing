# Collection APIs

**Collection** は提出物の追加・取得・検索の窓口。Storage（バイト）、Catalog（索引）、Locator（Filing → 相対パス）を束ねる。

## Public types

| Type                               | Description                                                                                                         |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [Collection](/docs/spec/api/Collections/Collection)         | Main entry: `add`, `get`, `get_filing`, `get_content`, `get_path`, `search`                                         |
| [Catalog](/docs/spec/api/Collections/Catalog)               | DuckDB-backed index; `index`, `get`, `search`, etc.                                                                 |
| [Storage](/docs/spec/api/Collections/Storage/Storage)       | Protocol: `save(content, storage_key?)`, `load_by_path(relative_path)`, `base_dir`                                  |
| [LocalStorage](/docs/spec/api/Collections/Storage/LocalStorage) | Storage implementation: saves under `base_dir`; `storage_key` is required                                           |
| [FilingResolver](/docs/spec/api/Collections/FilingResolver) | `_filing_class`（FQCN）→ Filing サブクラス; `default_resolver`, `register_filing_class` |

## Default setup

If `Collection()` is called without `storage` or `catalog`, it uses `.fino/collection` under the current working directory: `LocalStorage(base_dir)` and `Catalog(index.db)`.

## Flow

- **add(filing, content)**: Checks SHA256 vs `filing.checksum`, resolves path via Locator, indexes via Catalog (skip if same id), saves bytes via Storage. Returns `(filing, path)`.
- **get / get_filing / get_content / get_path**: Catalog for metadata, Locator for path, Storage for content.
- **search(expr, …)**: Catalog へ委譲。`expr` に `bool` を渡すと Catalog 側で `CatalogExprTypeError`。それ以外は [Collection Search](/docs/spec/Tutorial/Collection-Search) のとおり DuckDB WHERE にコンパイル。
