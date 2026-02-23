from fino_filing import Field


class TestField_Initialize:
    """
    Fieldのインスタンス化をテストする。
    - 正常系: 全ての引数が正常に設定されている場合
    - 正常系: 名前付き引数で設定する場合
    - 正常系: 引数なしでもインスタンス化できる
    - 正常系: immutable=True のフィールドを設定された場合
    """

    def test_field_initialize_with_positional_arguments(self) -> None:
        field = Field("test_field", str, True, True, False, "test_description")

        assert field.name == "test_field"
        assert field._field_type is str
        assert field.indexed is True
        assert field.immutable is True
        assert field.required is False
        assert field.description == "test_description"

    def test_field_initialize_with_named_arguments(self) -> None:
        field = Field(
            name="test_field",
            _field_type=str,
            indexed=True,
            immutable=True,
            required=True,
            description="test_description",
        )

        assert field.name == "test_field"
        assert field._field_type is str
        assert field.indexed is True
        assert field.immutable is True
        assert field.required is True
        assert field.description == "test_description"

    def test_field_initialize_without_optional_arguments(self) -> None:
        field = Field()

        assert field.name == ""
        assert field._field_type is None
        assert field.indexed is False
        assert field.immutable is False
        assert field.required is False
        assert field.description is None
