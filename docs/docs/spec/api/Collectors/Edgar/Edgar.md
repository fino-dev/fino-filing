---
sidebar_position: 0
title: Edgar
slug: Edgar
---

# Edgar（SEC）

共有の **EdgarConfig** / **EdgarClient** と、用途別 Collector 3 種類。

## Collectors

| クラス | 生成する Filing | 役割 |
| ------ | --------------- | ---- |
| **EdgarFactsCollector** | `EdgarCompanyFactsFiling` | Submissions メタ + Company Facts JSON |
| **EdgarArchiveCollector** | `EdgarArchiveFiling` | Archives から提出パッケージ（primary / full） |
| **EdgarBulkCollector** | `EdgarBulkFiling` | `companyfacts.zip` または `submissions.zip` |

コンストラクタはいずれも `(collection: Collection, config: EdgarConfig)`。内部で `EdgarClient(config)` を生成する。
