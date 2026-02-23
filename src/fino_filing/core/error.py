class FinoFilingException(Exception):
    """
    FinoFilingの基底例外。
    発生した例外のクラス名を自動的にメッセージに埋め込む。
    """

    def __init__(self, message: str = "An unexpected error occurred."):
        # メッセージの構成をここで一括管理
        # 例: [Fino] クラス名: メッセージ
        full_message = f"[Fino Filing] {message}"

        self.message = full_message

        # 親の Exception クラスに渡す
        super().__init__(full_message)
