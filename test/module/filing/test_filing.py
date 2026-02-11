from datetime import datetime

from fino_filing import Filing


class TestFiling_Initialize:
    def test_filing_init(self) -> None:
        datetime_now = datetime.now()

        filing = Filing(
            id="test_id",
            source="test_source",
            name="test_name",
            is_zip=True,
            created_at=datetime_now,
        )

        assert filing.id == "test_id"
        assert filing.source == "test_source"
        assert filing.name == "test_name"
        assert filing.is_zip is True
        assert filing.created_at == datetime_now

    def test_filing_init_with_lack_field(self) -> None:
        #       with pytest.raises(FilingValidationError):
        filing = Filing(
            id="test_id",
            source="test_source",
            name="test_name",
            is_zip=True,
        )

        print(filing)
