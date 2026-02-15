from datetime import datetime

from fino_filing import Filing
from fino_filing.filing.field import Field


class TestFiling_Field:
    """
    FilingのフィールドのDescriptorの振る舞いをテストする。
    - 正常系: フィールドが正常にインスタンス化されること
    - 正常系: Filingのfieldの属性が正常に設定されていること
    """

    def test_filing_field_get_success(self, datetime_now: datetime) -> None:
        filing = Filing(
            id="test_id",
            source="test_source",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            created_at=datetime_now,
        )

        assert filing.id == "test_id"
        assert filing.source == "test_source"
        assert filing.checksum == "test_checksum"
        assert filing.name == "test_name"
        assert filing.is_zip is True
        assert filing.created_at == datetime_now

    def test_filing_field_attribute_correctness(self, datetime_now: datetime) -> None:
        """Filingのフィールドがdescriptorとして正しく設定されていることを確認"""
        # クラス属性として Field を取得
        id_field = Filing.id
        assert isinstance(id_field, Field)
        assert id_field.name == "id"
        assert id_field.indexed is True
        assert id_field.immutable is True
        assert id_field.description == "Filing ID"

        source_field = Filing.source
        assert isinstance(source_field, Field)
        assert source_field.name == "source"
        assert source_field.indexed is True
        assert source_field.immutable is True
        assert source_field.description == "Data source"

        checksum_field = Filing.checksum
        assert isinstance(checksum_field, Field)
        assert checksum_field.name == "checksum"
        assert checksum_field.indexed is True
        assert checksum_field.immutable is False
        assert checksum_field.description == "SHA256 checksum"

        name_field = Filing.name
        assert isinstance(name_field, Field)
        assert name_field.name == "name"
        assert name_field.indexed is True
        assert name_field.immutable is True
        assert name_field.description == "File name"

        is_zip_field = Filing.is_zip
        assert isinstance(is_zip_field, Field)
        assert is_zip_field.name == "is_zip"
        assert is_zip_field.indexed is True
        assert is_zip_field.immutable is False
        assert is_zip_field.description == "ZIP flag"

        created_at_field = Filing.created_at
        assert isinstance(created_at_field, Field)
        assert created_at_field.name == "created_at"
        assert created_at_field.indexed is True
        assert created_at_field.immutable is True
        assert created_at_field.description == "Created timestamp"
