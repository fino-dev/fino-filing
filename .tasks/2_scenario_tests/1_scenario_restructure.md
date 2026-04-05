# Scenario test restructure

- `test/scenario/` をユースケース別ディレクトリ（`collection/`, `edgar/`, `edinet/`）に整理
- 外部API実呼び出しは行わずモックで検証（Bulk 等の重い経路はシナリオ対象外）
- `EdinetCollector.collect` / `iter_collect` で `document_type` が `_fetch_documents` に届くよう修正
- ドキュメント: `testing-strategy.md`, `test-matrix.md`, `scenarios.md`, `Test.md`, `Quick-start.md`, `test/README.md`
