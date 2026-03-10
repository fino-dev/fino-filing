---
sidebar_position: 3
title: EdgerFactsCollector
---

# EdgerFactsCollector

SEC XBRL CompanyFacts API および Submissions API から構造化データ（JSON）を収集して Collection に保存する。`BaseCollector` を継承。

## Constructor

```python
EdgerFactsCollector(
    collection: Collection,
    config: EdgerConfig,
) -> EdgerFactsCollector
```

内部で `EdgerClient(config)` を生成する。クライアントを外から渡さない。

## Methods

### collect

```python
collect(**criteria: Any) -> list[tuple[Filing, str]]
```

`BaseCollector` のテンプレートメソッド。`fetch_documents(**criteria)` を呼び、各 RawDocument を parse → build_filing → add_to_collection する。収集条件は `criteria` で渡す（例: `cik_list=`, `limit_per_company=`）。

### fetch_documents

```python
fetch_documents(
    *,
    cik_list: list[str] | None = None,
    limit_per_company: int | None = None,
    **kwargs: Any,
) -> Iterator[RawDocument]
```

- 各 CIK について Submissions API で企業情報を取得し、CompanyFacts API で JSON を取得する。
- **cik_list**: CIK のリスト。`None` または空なら何も yield しない。
- **limit_per_company**: 未使用（Facts は 1 企業あたり 1 件の companyfacts JSON）。
- **Yields**: `RawDocument`。`content` は JSON bytes、`meta` に `_origin="facts"` 等を格納。

### parse_response

```python
parse_response(raw: RawDocument) -> Parsed
```

`raw.meta` を EDGARFiling 用の Parsed 辞書に正規化する。

### build_filing

```python
build_filing(parsed: Parsed, raw: RawDocument) -> EDGARFiling
```

Parsed と `raw.content` から `EDGARFiling` を生成する。
