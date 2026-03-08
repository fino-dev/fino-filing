---
sidebar_position: 5
title: EDGARFiling
---

# EDGARFiling

Built-in Filing subclass for EDGAR (SEC) documents. Registered on `default_resolver` for Catalog restore. Used by `EdgerSecApi` and `EdgerBulkData`.

## Fixed field

- **source**: Always `"EDGAR"` (class attribute).

## Additional fields

| Field | Type | Description |
|-------|------|-------------|
| `cik` | str | Central Index Key |
| `accession_number` | str | Accession number |
| `company_name` | str | Company name |
| `form_type` | str | Form type (e.g. 10-K, 10-Q) |
| `filing_date` | datetime | Filing date |
| `period_of_report` | datetime | Period of report |
| `sic_code` | str | SIC code |
| `state_of_incorporation` | str | State of incorporation |
| `fiscal_year_end` | str | Fiscal year end |

## Constructor

Same as base `Filing`: pass core fields and any of the above. `id` and `created_at` may be omitted for auto-generation.
