# 異常系仕様（公開API ごとの例外・戻り値）

公開API 単位で「どの条件でどの例外／戻り値になるか」を一覧化する。テストはこの一覧の各項目に対応する。

## Filing / Field（メタクラス・初期化・set）

| 条件 | 結果 | 備考 |
|------|------|------|
| 必須フィールド（id, source, checksum 等）が欠けている | `FilingRequiredError`。`errors` / `fields` に不足内容を含む | |
| 必須フィールドに明示的 `None` を渡す | `FilingRequiredError` | |
| フィールドに型として不正な値を渡す | `FieldValidationError`。`field`, `expected_type`, `actual_type` を含む | |
| immutable フィールドを初期化後に変更しようとする | `FieldImmutableError`。`field`, `current_value`, `attempt_value` を含む | |
| 複数フィールドのバリデーションエラー | `FilingValidationError` または `FilingImmutableError`。`errors` / `fields` に複数含む | |
| default 付きフィールドは省略可能 | 正常。省略時は default 値 | |
| 拡張クラスで必須フィールドが欠けている | 上記と同様の例外 | |

## Filing（to_dict / from_dict）

| 条件 | 結果 | 備考 |
|------|------|------|
| from_dict で必須キーが欠けている | `FilingRequiredError` 等（from_dict_with_missing_fields_failed） | |
| from_dict で型が不正 | `FieldValidationError` 等（from_dict_with_invalid_type_failed） | |

## Collection.add

| 条件 | 結果 | 備考 |
|------|------|------|
| `content` の SHA256 が `filing.checksum` と不一致 | `CollectionChecksumMismatchError`。`filing_id`, `actual_checksum`, `expected_checksum` を含む | |
| 同一 id で既に add 済みのときに再度 add | 仕様: **上書き許容**。catalog の index はスキップし、storage には上書き保存。戻り値は `(filing, path)` | 現状実装に合わせて仕様として明文化 |

## Collection.get_filing / get_content / get

| 条件 | 結果 | 備考 |
|------|------|------|
| 存在しない id を指定 | `get_filing`: `None`。`get_content`: `None`。`get`: `(None, None, None)` | |

## Locator.resolve

| 条件 | 結果 | 備考 |
|------|------|------|
| 解決できない Filing（path が得られない） | `LocatorPathResolutionError`（Collection.add 内で raise） | |

## 例外のメッセージ形式

- 基底: `FinoFilingException`。`message` は接頭辞 `"[Fino Filing] "` を含む。
- `FilingValidationError` / `FilingImmutableError` / `FilingRequiredError`: `str(exception)` で `errors` を改行区切りで含む場合あり（仕様で保証するのは「含まれること」程度で可。完全一致は実装詳細にしない）。

## 参照

- テストとの対応: [test-matrix.md](test-matrix.md)
- 戦略: [testing-strategy.md](testing-strategy.md)
