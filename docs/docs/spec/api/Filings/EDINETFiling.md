---
sidebar_position: 4
title: EDINETFiling
---

# EDINETFiling

Built-in Filing subclass for EDINET documents. Registered on `default_resolver` for Catalog restore.

## Fixed field

- **source**: Always `"EDINET"` (class attribute).

## Additional fields

All are defined with `Field(...)`; none are `indexed` by default in the base definition.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `doc_id` | str | — | Doc ID (書類管理番号) |
| `edinet_code` | str | — | EDINET code |
| `sec_code` | str | — | Security code (証券コード) |
| `jcn` | str | — | Corporate number (法人番号) |
| `filer_name` | str | — | Filer name (提出者名) |
| `ordinance_code` | str | — | Ordinance code |
| `form_code` | str | — | Form code |
| `doc_type_code` | str | — | Document type code |
| `doc_description` | str | — | Document description |
| `period_start` | datetime | — | Period start |
| `period_end` | datetime | — | Period end |
| `submit_datetime` | datetime | — | Submit datetime |
| `parent_doc_id` | str \| None | None | Parent doc ID (optional) |

## Constructor

Same as base `Filing`: pass core fields (`name`, `checksum`, `format`, `is_zip`, etc.) and any of the above. `id` and `created_at` may be omitted for auto-generation.
