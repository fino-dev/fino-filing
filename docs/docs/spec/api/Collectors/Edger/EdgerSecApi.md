---
sidebar_position: 4
title: EdgerSecApi
---

# EdgerSecApi

Strategy that fetches filings from the SEC Company Submissions API, parses responses, and produces `EDGARFiling`. Used by `EdgerCollector`.

## Constructor

```python
EdgerSecApi(config: EdgerConfig) -> EdgerSecApi
```

## Methods

### fetch_documents

```python
fetch_documents(
    cik_list: list[str] | None = None,
    limit_per_company: int | None = None,
) -> Iterator[RawDocument]
```

- Calls SEC submissions API per CIK (`https://data.sec.gov/submissions/CIK{cik}.json`), then fetches each recent filing’s primary document (index page) from Archives.
- **cik_list**: List of CIKs (e.g. `["320193"]` for Apple). If `None` or empty, yields nothing.
- **limit_per_company**: Optional cap on number of filings per company.
- **Yields**: `RawDocument` with `content` (e.g. HTML) and `meta` including `cik`, `accession_number`, `company_name`, `form_type`, `filing_date`, `period_of_report`, `primary_name`, `_origin="sec"`, etc.
- Network/parse errors for a CIK or a single filing are logged and skipped; iteration continues.

### parse_response

```python
parse_response(raw: RawDocument) -> Parsed
```

Maps `raw.meta` to the Parsed dict expected by `to_filing` (same keys as EDGARFiling fields: `cik`, `accession_number`, `company_name`, `form_type`, `filing_date`, `period_of_report`, etc., plus `primary_name`).

### to_filing

```python
to_filing(parsed: Parsed, content: bytes) -> EDGARFiling
```

Builds `EDGARFiling` from `parsed` and `content` (checksum is computed from `content`). Used by `EdgerCollector.build_filing` for SEC-origin raw documents.
