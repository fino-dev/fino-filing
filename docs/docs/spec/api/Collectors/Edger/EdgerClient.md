---
sidebar_position: 2
title: EdgerClient
---

# EdgerClient

EDGAR 全エンドポイント用の共通 HTTP クライアント。**Collector の内部**で `EdgerConfig` から生成され、直接ユーザーがインスタンス化する必要はない。レート制限（リクエスト間 delay）と 503 リトライを行う。

## Constructor

```python
EdgerClient(config: EdgerConfig) -> EdgerClient
```

## Methods

### get_submissions

```python
get_submissions(cik: str) -> dict[str, Any]
```

SEC Submissions API から企業の提出一覧を取得。失敗時は空 `{}` を返す。

### get_company_facts

```python
get_company_facts(cik: str) -> dict[str, Any]
```

SEC XBRL CompanyFacts API から企業の XBRL ファクトを取得。失敗時は空 `{}` を返す。

### get_filing_document

```python
get_filing_document(cik: str, accession: str) -> bytes
```

提出物の index ページ（例: `{accession}-index.htm`）を取得。失敗時は空 `b""` を返す。

### get_bulk

```python
get_bulk(url: str) -> bytes
```

指定 URL から Bulk データを bytes で取得。失敗時は空 `b""` を返す。
