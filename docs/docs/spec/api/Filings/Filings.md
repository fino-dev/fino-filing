# Filing APIs

**Filing** は書類モデルと検索 DSL（`Field` / `Expr`）。Collection / Catalog / Storage には依存しない。

## 公開クラス

| Type | 説明 |
| ---- | ---- |
| [Filing](/docs/spec/api/Filings/Filing) | コアフィールド + サブクラスで拡張するスキーマ |
| [Field](/docs/spec/api/Filings/Field) | 記述子と `Expr` 用 DSL |
| [Expr](/docs/spec/api/Filings/Expr) | Catalog 検索用 WHERE 抽象 |
| [EDINETFiling](/docs/spec/api/Filings/EDINETFiling) | EDINET 書類 |
| [EdgarArchiveFiling](/docs/spec/api/Filings/EdgarArchiveFiling) | SEC Archives 由来の提出単位 |
| [EdgarBulkFiling](/docs/spec/api/Filings/EdgarBulkFiling) | SEC bulk ZIP |
| [EdgarCompanyFactsFiling](/docs/spec/api/Filings/EDGARCompanyFactsFiling) | Company Facts JSON |

SEC 系の **source リテラルはすべて `"EDGAR"`**（大文字）。
