---
sidebar_position: 5
title: EDGARFiling
---

# EDGARFiling

Built-in Filing subclass for **one SEC filing** (Submissions filing row + Archives document), e.g. index.htm. Registered on `default_resolver` for Catalog restore. Used by `EdgerDocumentsCollector` and `EdgerBulkCollector` (when meta maps to a submission row). Company Facts JSON uses **`EDGARCompanyFactsFiling`** instead.

## Fixed field

- **source**: Always `"EDGAR"` (class attribute).

## Additional fields

| Field | Type | Description |
|-------|------|-------------|
| `cik` | str | Central Index Key |
| `accession_number` | str | Accession number |
| `filer_name` | str | Company name |
| `form_type` | str | Form type (e.g. 10-K, 10-Q) |
| `filing_date` | datetime | Filing date |
| `period_of_report` | datetime | Period of report |
| `sic_code` | str | SIC code |
| `state_of_incorporation` | str | State of incorporation |
| `fiscal_year_end` | str | Fiscal year end |

## Constructor

Same as base `Filing`: pass core fields and any of the above. `id` and `created_at` may be omitted for auto-generation.
