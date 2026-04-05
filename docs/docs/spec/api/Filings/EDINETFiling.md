---
sidebar_position: 4
title: EDINETFiling
---

# EDINETFiling

Built-in Filing subclass for EDINET documents. Registered on `default_resolver` for Catalog restore.

## Fixed field

- **source**: Always `"EDINET"` (class attribute).

## Additional fields

| Field | Type | 備考 |
|-------|------|------|
| `doc_id` | str | `indexed=True`, `identifier=True`, `required=True` |
| `edinet_code`, `sec_code`, `jcn`, `filer_name`, `fund_code` | str | |
| `ordinance_code`, `form_code`, `doc_type_code`, `doc_description` | str | |
| `period_start`, `period_end` | date | |
| `submit_datetime` | datetime | |
| `current_report_reason` | str | |
| `parent_doc_id` | str \| None | 既定 `None` |

## Constructor

Same as base `Filing`: pass core fields (`name`, `checksum`, `format`, `is_zip`, etc.) and any of the above. `id` and `created_at` may be omitted for auto-generation.
