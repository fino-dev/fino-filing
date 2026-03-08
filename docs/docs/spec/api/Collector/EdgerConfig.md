---
sidebar_position: 3
title: EdgerConfig
---

# EdgerConfig

Configuration for EDGAR SEC API and Bulk Data. Used by `EdgerSecApi` and `EdgerBulkData`. SEC requires a valid User-Agent header.

## Constructor / attributes

Dataclass with these attributes (all have defaults):

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `sec_api_base` | str | `"https://data.sec.gov"` | Base URL for SEC API (e.g. submissions) |
| `archives_base` | str | `"https://www.sec.gov/Archives/edgar"` | Base URL for filing content |
| `bulk_base` | str | `"https://www.sec.gov/Archives/edgar/daily-index"` | Base URL for bulk daily index |
| `timeout` | int | 30 | Request timeout (seconds) |
| `user_agent` | str | `"fino-filing/0.1.0 (compliance; contact: ...)"` | User-Agent header (required by SEC) |
| `request_delay_sec` | float | 0.2 | Delay between requests (rate limiting) |
| `retry_503_max` | int | 3 | Max retries on 503 |
| `retry_503_wait_sec` | float | 2.0 | Wait between 503 retries (seconds) |

Override `user_agent` when using in production (e.g. with your app name and contact).
