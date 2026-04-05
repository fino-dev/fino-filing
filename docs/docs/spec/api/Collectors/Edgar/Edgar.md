---
sidebar_position: 0
title: Edgar
slug: Edgar
---

# Edgar Abstruction

Edgar 用 Collector 群。単一の **EdgarClient** と **EdgarConfig** を共有し、用途別に 3 種類の Collector を提供する。

## Collectors

| クラス                      | 用途                                                   |
| --------------------------- | ------------------------------------------------------ |
| **EdgarFactsCollector**     | JSON CompanyFacts / Submissions から構造化データを収集 |
| **EdgarArchiveCollector** | 提出書類（htm / iXBRL）を収集                          |
| **EdgarBulkCollector**      | Bulk 一括データ用（現状スタブ）                        |

## Components

| クラス          | 用途                                              |
| --------------- | ------------------------------------------------- |
| **EdgarConfig** | ユーザー設定（User-Agent 用メール・タイムアウト） |
| **EdgarClient** | 共通 HTTP クライアント（Collector の内部で使用）  |

各 Collector は `BaseCollector` を継承し、`collect(**criteria)` で収集条件（`cik_list`, `limit_per_company` 等）を渡す。コンストラクタは `(collection, config)` のみで、内部で `EdgarClient(config)` を生成する。
