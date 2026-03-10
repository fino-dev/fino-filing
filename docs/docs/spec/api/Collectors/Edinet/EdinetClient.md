---
sidebar_position: 2
title: EdinetClient
---

# EdinetClient

**内部コンポーネント**。EDINET 書類一覧API・書類取得API のリクエスト実行と共通処理（レート制限・リトライ・Subscription-Key ヘッダ）を行う。ユーザーが直接インスタンス化する必要はなく、`EdinetCollector` に `EdinetConfig` を渡すと内部で利用される。

## メソッド（参考）

| メソッド | 説明 |
|----------|------|
| `get_document_list(date: str, type: int = 1) -> dict` | 書類一覧取得API を実行し、レスポンス JSON をそのまま返す。失敗時は空 dict。 |
| `get_document(doc_id: str, type: int = 1) -> bytes` | 書類取得API で doc_id に紐づく書類実体を取得する。失敗時は空 bytes。 |
