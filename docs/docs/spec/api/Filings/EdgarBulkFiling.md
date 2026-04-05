---
sidebar_position: 6
title: EdgarBulkFiling
---

# EdgarBulkFiling

SEC の **bulk ZIP**（`companyfacts.zip` / `submissions.zip`）1 ファイルを表す組み込み `Filing`。`default_resolver` に登録済み。`EdgarBulkCollector` が生成する。

## 固定値

- **source**: `"EDGAR"`
- **edgar_resource_kind**: `"bulk"`
- **format**: `"json"`（論理上の分類; 実体は ZIP）
- **is_zip**: `True`

## 追加フィールド

| Field | 備考 |
| ----- | ---- |
| `bulk_type`, `bulk_date` | `identifier=True`（id 自動生成に使用） |

## コンストラクタ

基底 `Filing` と同様。`id` / `created_at` は省略可。
