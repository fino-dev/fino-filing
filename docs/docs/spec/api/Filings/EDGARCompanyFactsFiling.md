---
sidebar_position: 6
title: EdgarCompanyFactsFiling
---

# EdgarCompanyFactsFiling

Built-in Filing subclass for **one Company Facts API** response (`/api/xbrl/companyfacts/CIKxxx.json`). Registered on `default_resolver` for Catalog restore. Used by `EdgarFactsCollector`.

## Fixed field

- **source**: Always `"Edgar"` (class attribute; same literal as `EdgarFiling` for cross-source queries).

## Additional fields

| Field | Type | Description |
|-------|------|-------------|
| `cik` | str | Central Index Key |
| `filer_name` | str | Company name (from Submissions API) |
| `sic_code` | str | SIC code or description |
| `state_of_incorporation` | str | State of incorporation |
| `fiscal_year_end` | str | Fiscal year end |

Submission-specific fields (`accession_number`, `form_type`, `filing_date`, `period_of_report`) are **not** on this type.

## Constructor

Same as base `Filing`: pass core fields and any of the above. `id` and `created_at` may be omitted for auto-generation.
