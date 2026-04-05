---
sidebar_position: 2
title: EdgarClient
---

# EdgarClient

SEC（`data.sec.gov` / `www.sec.gov/Archives/edgar`）向け HTTP。**Collector 内部**で `EdgarConfig` から生成される。`HttpClient` 経由でレート制限・リトライを行う。

## Constructor

```python
EdgarClient(config: EdgarConfig, *, _http_client: HttpClient | None = None) -> EdgarClient
```

## Methods

| Method | 戻り値 | 説明 |
| ------ | ------ | ---- |
| `get_submissions(cik: str)` | `dict[str, Any]` | `submissions/CIK{cik}.json` |
| `get_company_facts(cik: str)` | `dict[str, Any]` | `api/xbrl/companyfacts/CIK{cik}.json` |
| `get_archives_file(cik, accession, relative_path)` | `bytes` | Archives 配下の 1 ファイル |
| `try_get_filing_index_json(cik, accession)` | `dict \| None` | `index.json` が無い提出は `None`（404 相当） |
| `get_bulk(type)` | `bytes` | `type` は `"companyfacts"` \| `"submissions"`。対応 ZIP を生バイトで取得 |

HTTP エラー・レート制限等は `HttpRequestError` / `HttpRateLimitError` / `HttpNotFoundError` 等にマッピングされる（空 dict を返す仕様ではない）。
