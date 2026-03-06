# fino-filing ドキュメント（Docusaurus）

このサイトは [Docusaurus](https://docusaurus.io/) でビルドしています。

## ドキュメント構成

- **`docs/spec/`** … 仕様（利用者向け）: 概要・クイックスタート・API契約・シナリオ
- **`docs/dev/`** … 開発（開発者向け）: 設計・テスト・アーカイブ

仕様と開発を分け、両方とも Web で閲覧できます。追加する場合はどちらに属するかで `spec/` か `dev/` のどちらかに配置してください。

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
