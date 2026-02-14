from fino_filing import Field


class TestField_Initialize:
    def test_field_initialize_success(self) -> None:
        field = Field("test_field", str, indexed=True, description="test_description")
        assert field.name == "test_field"
        assert field.field_type is str
        assert field.indexed is True
        assert field.description == "test_description"
