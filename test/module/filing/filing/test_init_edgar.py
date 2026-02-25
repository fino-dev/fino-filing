"""EDGARFiling の初期化テスト。観点: 正常系"""

from datetime import datetime

from fino_filing import EDGARFiling


class TestFiling_Initialize_EDGAR:
    """EDGARFiling. 観点: 正常系（初期化）"""

    def test_filing_initialize_edgar_success(self) -> None:
        """EDGARFiling を必須フィールドで初期化できる"""
        datetime_now = datetime.now()
        edgar_filing = EDGARFiling(
            id="edgar_id",
            source="EDGAR",
            checksum="a" * 64,
            name="10-K.xbrl",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
            cik="0001234567",
            accession_number="0001234567-24-000001",
            company_name="Test Corp",
            form_type="10-K",
            filing_date=datetime_now,
            period_of_report=datetime_now,
            sic_code="7370",
            state_of_incorporation="DE",
            fiscal_year_end="12-31",
        )
        assert edgar_filing.id == "edgar_id"
        assert edgar_filing.source == "EDGAR"
        assert edgar_filing.checksum == "a" * 64
        assert edgar_filing.name == "10-K.xbrl"
        assert edgar_filing.cik == "0001234567"
        assert edgar_filing.company_name == "Test Corp"
        assert edgar_filing.form_type == "10-K"
