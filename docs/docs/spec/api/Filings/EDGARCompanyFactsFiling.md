---
sidebar_position: 7
title: EdgarCompanyFactsFiling
---

# EdgarCompanyFactsFiling

**Company Facts API** の JSON スナップショット 1 件（`/api/xbrl/companyfacts/CIKxxx.json`）。`default_resolver` 登録済み。`EdgarFactsCollector` が生成する。

## 固定値

- **source**: `"EDGAR"`
- **edgar_resource_kind**: `"companyfacts"`
- **format**: `"json"` / **is_zip**: `False`

## 追加フィールド（主）

| Field | 備考 |
| ----- | ---- |
| `cik` | `identifier=True` |
| `entity_type`, `filer_name`, `sic`, `sic_description`, `filer_category` | Submissions メタ |
| `state_of_incorporation`, `fiscal_year_end` | |
| `tickers_key`, `exchanges_key` | 正規化済みパイプ区切り |

提出 1 件単位の `accession_number` / `form` 等はこの型には含めない。

## コンストラクタ

基底 `Filing` と同様。`id` / `created_at` は省略可。
