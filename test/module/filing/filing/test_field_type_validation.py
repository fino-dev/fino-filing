# from datetime import datetime

# from fino_filing import Filing


# class TestFiling_FieldTypeValidation:
#     def test_filing_field_type_success(self) -> None:
#         filing = Filing(
#             id="test_id",
#             source="test_source",
#             checksum="test_checksum",
#             name="test_name",
#             is_zip=True,
#             created_at=datetime.now(),
#         )
#         assert isinstance(filing.id, str)
#         assert isinstance(filing.source, str)
#         assert isinstance(filing.checksum, str)
#         assert isinstance(filing.name, str)
#         assert isinstance(filing.is_zip, bool)
#         assert isinstance(filing.created_at, datetime)
