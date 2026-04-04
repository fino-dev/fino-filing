---
sidebar_position: 3
title: EdgarFactsCollector
---

# EdgarFactsCollector

SEC XBRL CompanyFacts API および Submissions API から構造化データ（JSON）を収集して Collection に保存する。`BaseCollector` を継承。

## Constructor

```python
EdgarFactsCollector(
    collection: Collection,
    config: EdgarConfig,
) -> EdgarFactsCollector
```

内部で `EdgarClient(config)` を生成する。クライアントを外から渡さない。

## Methods

### collect

```python
collect(**criteria: Any) -> list[tuple[EdgarCompanyFactsFiling, str]]
```

`BaseCollector` のテンプレートメソッド。`_fetch_documents(**criteria)` を呼び、各 RawDocument を `_parse_response` → `_build_filing` → add_to_collection する。収集条件は `criteria` で渡す（例: `cik_list=`, `limit=`）。

### _fetch_documents

```python
_fetch_documents(
    *,
    cik_list: list[str] | None = None,
    limit: int | None = None,
) -> Iterator[RawDocument]
```

- 各 CIK について Submissions API で企業メタを取得し、CompanyFacts API で JSON を取得する。
- **cik_list**: CIK のリスト。`None` または空なら何も yield しない。
- **limit**: 予約（現状未使用。1 企業あたり 1 件の companyfacts JSON）。
- **Yields**: `RawDocument`。`content` は JSON bytes、`meta` に会社属性と `_origin="facts"` 等を格納（accession / form は含めない）。

### _parse_response

```python
_parse_response(meta: Meta) -> Parsed
```

`meta` を `EdgarCompanyFactsFiling` 用の Parsed 辞書に正規化する。

### _build_filing

```python
_build_filing(parsed: Parsed, content: bytes) -> EdgarCompanyFactsFiling
```

Parsed と `content` から `EdgarCompanyFactsFiling` を生成する。
