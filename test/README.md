# テスト

## ディレクトリ構成

- **test/module/** … 単体テストおよび結合テスト（Collection はファサードのため結合テストとしてここに配置）
  - core, filing, field, collection, locator など、公開API に対応したモジュール別
- **test/scenario/** … シナリオテスト（利用者ユースケースごとに独立したファイル。外部API実呼び出しは行わない）

## 実行方法

```bash
pytest
```

単体のみ（Collection を含む結合テストを除く）は、マーカーを導入している場合は `pytest -m "not integration"` で可能（任意）。

## どのファイルでどこまで確認しているか

公開API×観点の概要は [test-matrix](/docs/dev/design/test-matrix) を参照。

異常系の仕様は [Exception](/docs/spec/api/Exception)、テスト戦略は [testing-strategy](/docs/dev/design/testing-strategy) を参照。
