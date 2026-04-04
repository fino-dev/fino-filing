---
sidebar_position: 5
title: EdgarBulkCollector
---

# EdgarBulkCollector

SEC Bulk データを一括取得して Collection に保存する。`BaseCollector` を継承。**現状はスタブ**で、`_fetch_documents` は何も yield しない。

## 想定仕様（将来実装）

- **データソース**: SEC の daily-index 等。`EdgarClient.get_bulk(url)` で指定 URL から bytes を取得する。
- **収集条件**: `date_from` / `date_to` で日付範囲、`cik_list` で CIK フィルタ、`limit` で件数上限を想定。URL は package 側で daily-index の形式に合わせて構築する。
- **RawDocument の単位**: 一括取得結果（ZIP や TSV 等）を 1 件ずつに分割し、各単位で `RawDocument` を yield する想定。`meta` に `_origin="bulk"` および URL・日付等を格納する。

## Constructor

```python
EdgarBulkCollector(
    collection: Collection,
    config: EdgarConfig,
) -> EdgarBulkCollector
```

内部で `EdgarClient(config)` を生成する。

## Methods

### collect

```python
collect(**criteria: Any) -> list[tuple[EdgarFiling, str]]
```

`BaseCollector` のテンプレートメソッド。収集条件は `criteria` で渡す（将来: `date_from`, `date_to`, `cik_list`, `limit` 等）。

### _fetch_documents

```python
_fetch_documents(
    *,
    date_from: str | None = None,
    date_to: str | None = None,
    cik_list: list[str] | None = None,
    limit: int | None = None,
    **kwargs: Any,
) -> Iterator[RawDocument]
```

**現状**: 空イテレータを返す。上記パラメータは将来の Bulk 実装用に予約。

### _parse_response

```python
_parse_response(meta: Meta) -> Parsed
```

`meta` を `EdgarFiling` 用の Parsed 辞書に正規化する。Bulk 由来の `meta` も提出行ベースの Parsed 形に揃える。

### _build_filing

```python
_build_filing(parsed: Parsed, content: bytes) -> EdgarFiling
```

Parsed と `content` から `EdgarFiling` を生成する。
