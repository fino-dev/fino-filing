---
sidebar_position: 4
title: EdgerArchivesCollector
---

# EdgerArchivesCollector

SEC **Archives** 上の提出ファイルを、Submissions API の行に対応させて `Collection` に保存する。`BaseCollector` を継承。`EdgerFactsCollector`（Company Facts JSON）と役割が分かれる。

## Constructor

```python
EdgerArchivesCollector(
    collection: Collection,
    config: EdgerConfig,
    *,
    fetch_mode: EdgerArchivesFetchMode = "primary",
) -> EdgerArchivesCollector
```

- **fetch_mode**
  - `filing_index`: 従来どおり `{accession}-index.htm` のみ。
  - `primary`（既定）: Submissions の `primaryDocument` を優先し、失敗時は `data.sec.gov` の `{accession}-index.json` から本文候補を選び、最後に `-index.htm`。
  - `xbrl_bundle`: `index.json` 上の `.xml` / `.htm` / `.html` / `.xhtml`（`-index.htm` 除く）を **1 ファイルごと**に取得（Arelle 等向け）。

内部で `EdgerClient(config)` を生成する。

## EdgerDocumentsCollector（後方互換）

`EdgerDocumentsCollector` は `EdgerArchivesCollector` のサブクラスで、**既定の `fetch_mode` は `filing_index`**（旧挙動）。新規コードでは `EdgerArchivesCollector` と明示的な `fetch_mode` を推奨する。

## Methods

### collect / iter_collect

`BaseCollector` のテンプレートメソッド。`collect(**criteria)` の `criteria` に `cik_list`, `limit_per_company` に加え、**呼び出しごとに `fetch_mode` を上書き**できる。

### _fetch_documents

- **cik_list**: CIK のリスト。`None` または空なら何も yield しない。
- **limit_per_company**: 1 企業あたりの **提出（accession）行**の上限。`xbrl_bundle` のときは 1 提出あたり複数 `RawDocument` になり得る。
- **Yields**: `RawDocument`。`meta` に `_origin="archives"`、`archives_fetch_mode`、`primary_name`（保存上のファイル名）等。
