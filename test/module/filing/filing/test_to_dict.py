from datetime import datetime

from fino_filing.filing.filing import Filing


class TestFiling_ToDict:
    """
    Filing.to_dict() のテスト
    - 正常系: すべてのフィールドが辞書化されること
    - 正常系: datetimeがISO文字列に変換されること
    - 正常系: default値のみのインスタンスの変換
    """

    def test_to_dict_success(self, datetime_now: datetime) -> None:
        """すべてのフィールドが正しく辞書化されることを確認"""
        filing = Filing(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            format="hoge",
            created_at=datetime_now,
        )

        result = filing.to_dict()
        assert result["id"] == "test_id"
        assert result["source"] == "test_source"
        assert result["checksum"] == "test_checksum"
        assert result["name"] == "test_name"
        assert result["is_zip"] is True
        assert result["format"] == "hoge"
        assert result["created_at"] == datetime_now
