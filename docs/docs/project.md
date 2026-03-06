# fino-filing

## 概要

fino-filing は、EDINET API を利用して開示書類を効率的に収集・検索・ダウンロードするための Python ライブラリである。

OSS利用者・データ分析者・Pythonエンジニアを主な利用者と想定する。

CLIは提供せず、Pythonコードから `import fino_filing` して利用するライブラリとして提供する。

**現状の実装**: Collection / Catalog / LocalStorage / Filing（EDINET・EDGAR 拡張含む）によるローカルストアへの追加・検索・取得が利用可能。API連携（EDINET クライアント・収集）は今後実装予定。

---

## 目的

- EDINET EDGER APIを簡単に扱えるクライアントを提供する（今後実装）
- 書類一覧APIの結果を内部データストアに同期し、柔軟な検索を可能にする
- 企業別・期間別・書類種別など多様な条件でドキュメントを収集可能にする
- 保存先・保存構造は利用者が自由に制御できるよう設計する

---

## 利用イメージ
