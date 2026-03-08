---
sidebar_position: 1
title: Filing
---

# Filing

Document model with a metaclass-defined schema. Core fields are fixed; subclasses add fields via `Annotated[str, Field(...)]`.

## Constructor

```python
Filing(**kwargs) -> Filing
```

- **kwargs**: Field values (e.g. `source`, `name`, `checksum`, `format`, `is_zip`). Omit `id` and `created_at` to have them auto-generated.
- **Raises**: `FilingRequiredError` if a required field is missing or `None`; `FilingValidationError` / `FieldValidationError` on type mismatch; `FieldImmutableError` when reassigning an immutable field after init.

## Identity and ID generation

- **Identity fields**: Core set `source`, `name`, `is_zip`, `format` plus all user-defined fields (excluding `id`, `created_at`, `checksum`). Used for deterministic `id` generation.
- **id**: If not provided, computed as SHA256(identity field values)[:32].
- **created_at**: If not provided, set to `datetime.now()`.

## Instance methods

| Method          | Returns          | Description                                    |
| --------------- | ---------------- | ---------------------------------------------- |
| `to_dict()`     | `dict[str, Any]` | Flat dict of all fields; datetime → ISO string |
| `get(key: str)` | `Any`            | Value for `key`                                |

## Class methods

| Method                                  | Returns                    | Description                                                                                         |
| --------------------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------- |
| `from_dict(cls, data: dict) -> Self`    | Filing instance            | Restore from dict; datetime strings are parsed. Raises same as constructor when keys/types invalid. |
| `get_identity_fields(cls) -> list[str]` | Sorted list of field names | Fields used for ID generation                                                                       |
| `get_indexed_fields(cls) -> list[str]`  | List of field names        | Fields stored as physical columns in Catalog (indexed=True)                                         |

## Attributes (core)

All filings have these fields. Required unless noted.

| Field        | Type     | Required | Indexed | Immutable | Description                                                |
| ------------ | -------- | -------- | ------- | --------- | ---------------------------------------------------------- |
| `id`         | str      | yes      | yes     | yes       | Filing ID (auto-generated from identity fields if omitted) |
| `source`     | str      | yes      | yes     | yes       | Data source (e.g. "EDGAR", "EDINET")                       |
| `checksum`   | str      | yes      | yes     | no        | SHA256 hex digest of content                               |
| `name`       | str      | yes      | yes     | yes       | File name                                                  |
| `is_zip`     | bool     | yes      | yes     | no        | Whether content is ZIP                                     |
| `format`     | str      | yes      | yes     | yes       | Format / extension (e.g. xbrl, zip, pdf)                   |
| `created_at` | datetime | yes      | yes     | yes       | Created timestamp (auto-generated if omitted)              |

`id` is derived from identity fields (source, name, is_zip, format plus any user-defined fields); `created_at` defaults to `datetime.now()` when omitted.

## Custom Filing subclasses

You can define your own Filing type by subclassing `Filing` and declaring additional fields with `Annotated[str, Field(...)]` (or other types). The metaclass handles schema registration, identity, and validation. Register your subclass on a `FilingResolver` (e.g. used by Catalog) so instances can be restored from storage.

By default, the package provides two built-in subclasses that follow this pattern: **EDINETFiling** (source `"EDINET"`) and **EDGARFiling** (source `"EDGAR"`). They add source-specific fields (e.g. `doc_id`, `edinet_code` for EDINET; `cik`, `accession_number`, `form_type` for EDGAR) and are registered on the default resolver for Catalog restore.
