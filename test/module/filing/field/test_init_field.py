from fino_filing import Field


class TestField_Initialize:
    """
    Fieldのインスタンス化をテストする。
    - 正常系: 全ての引数が正常に設定されている場合
    - 正常系: 位置引数で設定初期化
    - 正常系: _field_type やimmutableのoptionalを含めずともインスタンス化できる
    - 正常系: immutable=True のフィールドを設定された場合
    """

    def test_field_initialize_success(self) -> None:
        field = Field("test_field", str, True, True, "test_description")

        assert field.name == "test_field"
        assert field._field_type is str
        assert field.indexed is True
        assert field.immutable is True
        assert field.description == "test_description"

    def test_field_initialize_with_positional_arguments(self) -> None:
        field = Field("test_field", str, True, True, "test_description")

        assert field.name == "test_field"
        assert field._field_type is str
        assert field.indexed is True
        assert field.immutable is True
        assert field.description == "test_description"
