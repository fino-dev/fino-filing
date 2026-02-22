from fino_filing.filing.filing import Filing


class Locator:
    """
    Locator (Filing Path Resolver<Strategy>)

    責務:
        - Filing metadata → storage path変換
        - 保存戦略の実装
        - パーティション戦略

    Filingの内容は知らない（metadataのみ使用）
    """

    def resolve(self, filing: Filing) -> str:
        """
        Filing metadata → storage path変換（partition + ファイル名 + 拡張子）。
        拡張子は Filing.is_zip に応じて .zip または .xbrl とする。
        """
        base = f"{filing.source or '_'}/{filing.id or '_'}"
        suffix = ".zip" if filing.is_zip else ".xbrl"
        return base + suffix
