# fino-filing

## 概要

fino-filing は、EDINET API を利用して開示書類を効率的に収集・検索・ダウンロードするための Python ライブラリである。

OSS利用者・データ分析者・Pythonエンジニアを主な利用者と想定する。

CLIは提供せず、Pythonコードから import して利用するライブラリとして提供する。

---

## 目的

- EDINET APIを簡単に扱えるクライアントを提供する
- 書類一覧APIの結果を内部データストアに同期し、柔軟な検索を可能にする
- 企業別・期間別・書類種別など多様な条件でドキュメントを収集可能にする
- 保存先・保存構造は利用者が自由に制御できるよう設計する

---

## 利用イメージ

```python
from fino_edinet import Edinet

client = Edinet(api_key="xxx")

client.sync()

docs = client.search(company="トヨタ", doc_type="有価証券報告書")
client.download(docs, path="./data")
```

利用者は基本的に Facade クラス（Edinet）経由で操作する。
