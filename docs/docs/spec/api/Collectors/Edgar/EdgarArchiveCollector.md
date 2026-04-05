---
sidebar_position: 4
title: EdgarArchiveCollector
---

# EdgarArchiveCollector

SEC Archives から提出書類（htm / iXBRL）を収集して Collection に保存する。`BaseCollector` を継承。

## Constructor

```python
EdgarArchiveCollector(
    collection: Collection,
    config: EdgarConfig,
) -> EdgarArchiveCollector
```

内部で `EdgarClient(config)` を生成する。

## Methods

### collect

```python
collect(**criteria: Any) -> list[tuple[EdgarFiling, str]]
```

`BaseCollector` のテンプレートメソッド。収集条件は `criteria` で渡す（例: `cik_list=`, `limit_per_company=`）。

### _fetch_documents

```python
_fetch_documents(
    *,
    cik_list: list[str] | None = None,
    limit_per_company: int | None = None,
    **kwargs: Any,
) -> Iterator[RawDocument]
```

- 各 CIK で Submissions API から accession 一覧を取得し、各提出物の index ページ（htm）を取得する。
- **cik_list**: CIK のリスト。`None` または空なら何も yield しない。
- **limit_per_company**: 1 企業あたりの提出件数上限。
- **Yields**: `RawDocument`。`content` は HTML bytes、`meta` に `_origin="documents"` 等を格納。

### _parse_response

```python
_parse_response(meta: Meta) -> Parsed
```

`meta` を `EdgarFiling` 用の Parsed 辞書に正規化する。

### _build_filing

```python
_build_filing(parsed: Parsed, content: bytes) -> EdgarFiling
```

Parsed と `content` から `EdgarFiling` を生成する。
