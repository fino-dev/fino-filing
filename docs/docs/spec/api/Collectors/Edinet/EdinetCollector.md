---
sidebar_position: 1
title: EdinetCollector
---

# EdinetCollector

EDINET の書類一覧APIで一覧を取得し、書類取得APIで実体を取得して Collection に保存する。`BaseCollector` を継承。ユーザーは `EdinetConfig` のみ渡し、内部で `EdinetClient` を生成する。

## Constructor

```python
EdinetCollector(
    collection: Collection,
    config: EdinetConfig,
) -> EdinetCollector
```

- **collection**: 書類と Filing を保存する Collection。
- **config**: EDINET API 用設定（API キー・タイムアウト）。api_base は不要。

## Methods

### collect

```python
collect(**criteria: Any) -> list[tuple[Filing, str]]
```

`BaseCollector` のテンプレートメソッド。収集条件は `criteria` で渡す（`date_from`, `date_to`, `limit` 等）。

### fetch_documents

```python
fetch_documents(
    *,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int | None = None,
    list_type: int = 2,
    **kwargs: Any,
) -> Iterator[RawDocument]
```

書類一覧APIで `date_from` 〜 `date_to` の日付範囲を 1 日ずつ取得し、各日の結果について書類取得APIで実体を取得して `RawDocument` を yield する。`date_from` が無い場合は何も返さない。`limit` で件数上限を指定可能。`list_type` は一覧APIの type（1=メタデータのみ、2=メタデータ+書類一覧）。

### parse_response

```python
parse_response(raw: RawDocument) -> Parsed
```

`raw.meta` を EDINETFiling 用の Parsed 辞書に正規化する。

### build_filing

```python
build_filing(parsed: Parsed, raw: RawDocument) -> EDINETFiling
```

Parsed と `raw.content` から [EDINETFiling](../../Filings/EDINETFiling) を生成する。
