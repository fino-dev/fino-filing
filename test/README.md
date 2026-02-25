# テスト

## ディレクトリ構成

- **test/module/** … 単体テストおよび結合テスト（Collection はファサードのため結合テストとしてここに配置）
  - core, filing, field, collection, locator など、公開API に対応したモジュール別
- **test/scenario/** … シナリオテスト（利用者目線の一連の流れ）。現状はコメントアウトまたは skip あり

## 実行方法

```bash
pytest
```

単体のみ（Collection を含む結合テストを除く）は、マーカーを導入している場合は `pytest -m "not integration"` で可能（任意）。

## どのファイルでどこまで確認しているか

公開API×観点ごとの対応は **docs/design/test-matrix.md** を参照。

異常系の仕様は **docs/design/exception-spec.md**、テスト戦略は **docs/design/testing-strategy.md** を参照。
