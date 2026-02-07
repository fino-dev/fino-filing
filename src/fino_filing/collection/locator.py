from fino_filing import Filing


class Locator:
    """
    Path解決戦略

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
