from datetime import datetime

from fino_filing.filing.filing_edinet import EDINETFiling


class TestFiling_Initialize_EDINET:
    def test_filing_initialize_edinet_success(self) -> None:
        datetime_now = datetime.now()
        edinet_filing = EDINETFiling(
            id="test_id",
            checksum="test_checksum",
            name="test_name",
            is_zip=True,
            created_at=datetime_now,
            edinet_code="test_edinet_code",
            sec_code="test_sec_code",
            jcn="test_jcn",
            filer_name="test_filer_name",
            ordinance_code="test_ordinance_code",
            form_code="test_form_code",
            doc_type_code="test_doc_type_code",
            doc_description="test_doc_description",
            period_start=datetime_now,
            period_end=datetime_now,
            submit_datetime=datetime_now,
            parent_doc_id="test_parent_doc_id",
        )

        assert edinet_filing.id == "test_id"
        assert edinet_filing.source == "EDINET"
        assert edinet_filing.checksum == "test_checksum"
        assert edinet_filing.name == "test_name"
        assert edinet_filing.is_zip is True
        assert edinet_filing.created_at == datetime_now
        assert edinet_filing.edinet_code == "test_edinet_code"
        assert edinet_filing.sec_code == "test_sec_code"
        assert edinet_filing.jcn == "test_jcn"
        assert edinet_filing.filer_name == "test_filer_name"
        assert edinet_filing.ordinance_code == "test_ordinance_code"
        assert edinet_filing.form_code == "test_form_code"
        assert edinet_filing.doc_type_code == "test_doc_type_code"
        assert edinet_filing.doc_description == "test_doc_description"
        assert edinet_filing.period_start == datetime_now
        assert edinet_filing.period_end == datetime_now
        assert edinet_filing.submit_datetime == datetime_now
        assert edinet_filing.parent_doc_id == "test_parent_doc_id"
