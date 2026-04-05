---
sidebar_position: 5
title: EdgarArchiveFiling
---

# EdgarArchiveFiling

SEC Submissions と Archives から取得した**1 件の提出単位**（primary または full パッケージ）を表す組み込み `Filing`。`default_resolver` に登録済み。`EdgarArchiveCollector` が生成する。

## 固定値

- **source**: `"EDGAR"`
- **edgar_resource_kind**: `"archive"`

## 主な追加フィールド（検索用）

| Field | 備考 |
| ----- | ---- |
| `cik`, `accession_number` | `identifier=True`（id 自動生成に使用） |
| `edgar_resource_kind`, `tickers_key`, `exchanges_key`, `form` 等 | 提出メタ・インデックス用 |

日付系は `filing_date` / `report_date`（`date`）、`acceptance_date_time`（`datetime`）。取得モードは `EdgarDocumentsFetchMode`（`PRIMARY_ONLY` / `FULL`）に応じて内容と `name` が変わる。

## コンストラクタ

基底 `Filing` と同様。`id` / `created_at` は省略可（識別フィールドから自動生成）。
