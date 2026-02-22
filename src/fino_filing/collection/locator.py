from fino_filing.filing.filing import Filing


def _suffix(filing: Filing) -> str:
    """
    Filing の is_zip / format から拡張子を決定する。
    """
    # is_zip が True のときは .zip
    if getattr(filing, "is_zip", False):
        return ".zip"
    # format が設定されていればそれを使用（サニタイズを行う）
    fmt = (getattr(filing, "format", None) or "").strip().lstrip(".").lower()
    # 英数字以外の文字が含まれていないかどうかをチェック
    if fmt and all(c.isalnum() or c in "-_" for c in fmt):
        return f".{fmt}"
    # 許容される拡張子がない場合は空文字列
    return ""


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
