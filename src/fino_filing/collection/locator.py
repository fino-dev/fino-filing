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
        Filing metadata → storage path変換
        """
        return f"{filing.source}/{filing.id}"
