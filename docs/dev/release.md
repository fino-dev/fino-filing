# リリース（PyPI）

パッケージのバージョンは `pyproject.toml` ではなく [uv-dynamic-versioning](https://github.com/ninoseki/uv-dynamic-versioning) により **Git タグ** から決まります（ビルドは [hatchling](https://github.com/pypa/hatch)）。

## 手順

1. **CD - Create Release Tag**（`workflow_dispatch`）を実行し、`bump` で **major / minor / patch** を選ぶ。
2. **`plan` ジョブ**で付与予定タグが計算され、実行サマリーに表示される。**内容を確認**したうえで **`apply` ジョブ**が続行し、タグが作成・push される。タグ名の計算ルール: 既存の **安定版**タグ（`X.Y.Z` または `vX.Y.Z`）の最大から bump。プレリリース（例: `0.2.0b1`）は基準外。該当タグが無い初回は `0.0.0` 相当から bump（例: minor → `v0.1.0`）。
3. タグ作成前に必ず人の承認で止めたい場合は、GitHub の **Settings → Environments** に `create-release-tag` を追加し、**Required reviewers** を設定する（未設定だと `plan` 完了後すぐ `apply` が走る）。
4. タグが `push` されると **CD - Deploy Package** が走り、`uv build` 後に PyPI へ公開される。

## PyPI 側の設定

- **Trusted publishing（推奨）**: PyPI でこのリポジトリ用の Trusted Publisher を登録し、Actions の OIDC で公開する（ワークフローは `id-token: write` を付与済み）。
- **API トークン**: Trusted Publisher を使わない場合は [pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish) の README に従い、`secrets.PYPI_API_TOKEN` を設定し、Deploy ジョブに `password` を渡すよう変更する。

## ローカルでのバージョン確認

```bash
uvx uv-dynamic-versioning
```
