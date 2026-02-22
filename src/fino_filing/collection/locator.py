from fino_filing.filing.filing import Filing


def _suffix(filing: Filing) -> str:
    """
    Filing の format または is_zip から拡張子を決定する。
    format が空でないかつサニタイズ済みならそれを使い、否則は is_zip で .zip / .xbrl。
    """
    fmt = (getattr(filing, "format", None) or "").strip().lstrip(".").lower()
    if fmt and all(c.isalnum() or c in "-_" for c in fmt):
        return f".{fmt}"
    return ".zip" if filing.is_zip else ".xbrl"


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
        拡張子は format が設定されていればそれを使用（サニタイズ済み）、
        空の場合は is_zip に応じて .zip または .xbrl とする。
        """
        base = f"{filing.source}/{filing.id}"
        return base + _suffix(filing)
