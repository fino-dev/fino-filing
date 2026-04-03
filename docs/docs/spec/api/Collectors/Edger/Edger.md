---
sidebar_position: 0
title: Edger
slug: Edger
---

# Edger Abstruction

EDGAR 用 Collector 群。単一の **EdgerClient** と **EdgerConfig** を共有し、用途別に 3 種類の Collector を提供する。

## Collectors

| クラス                      | 用途                                                   |
| --------------------------- | ------------------------------------------------------ |
| **EdgerFactsCollector**     | JSON CompanyFacts / Submissions から構造化データを収集 |
| **EdgerArchivesCollector** | Archives 提出ファイル（index / primary / XBRL バンドル）を収集 |
| **EdgerDocumentsCollector** | 後方互換: 既定 `filing_index`（`-index.htm` のみ）        |
| **EdgerBulkCollector**      | Bulk 一括データ用（現状スタブ）                        |

## Components

| クラス          | 用途                                              |
| --------------- | ------------------------------------------------- |
| **EdgerConfig** | ユーザー設定（User-Agent 用メール・タイムアウト） |
| **EdgerClient** | 共通 HTTP クライアント（Collector の内部で使用）  |

各 Collector は `BaseCollector` を継承し、`collect(**criteria)` で収集条件（`cik_list`, `limit_per_company` 等）を渡す。コンストラクタは `(collection, config)` のみで、内部で `EdgerClient(config)` を生成する。
