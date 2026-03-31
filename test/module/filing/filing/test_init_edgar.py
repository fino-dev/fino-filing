"""EDGARFiling の初期化テスト。観点: 正常系"""

from datetime import datetime

import pytest

from fino_filing import EDGARCompanyFactsFiling, EDGARFiling


@pytest.mark.module
@pytest.mark.filing
@pytest.mark.edger
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
            filer_name="Test Corp",
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
        assert edgar_filing.filer_name == "Test Corp"
        assert edgar_filing.form_type == "10-K"


@pytest.mark.module
@pytest.mark.filing
@pytest.mark.edger
class TestFiling_Initialize_EDGAR_CompanyFacts:
    """EDGARCompanyFactsFiling. 観点: 正常系（初期化）"""

    def test_filing_initialize_edgar_company_facts_success(self) -> None:
        """EDGARCompanyFactsFiling を必須フィールドで初期化できる"""
        datetime_now = datetime.now()
        f = EDGARCompanyFactsFiling(
            id="facts_id",
            source="EDGAR",
            checksum="b" * 64,
            name="CIK0001652044-companyfacts.json",
            is_zip=False,
            format="json",
            created_at=datetime_now,
            cik="0001652044",
            filer_name="Alphabet Inc.",
            sic="7370",
            sic_description="Services",
            filer_category="Large accelerated filer",
            state_of_incorporation="DE",
            fiscal_year_end="12-31",
            tickers_key="GOOGL",
            exchanges_key="Nasdaq",
        )
        assert f.id == "facts_id"
        assert f.cik == "0001652044"
        assert f.filer_name == "Alphabet Inc."
        assert f.format == "json"
        assert f.edgar_resource_kind == "companyfacts"

    def test_filing_initialize_edgar_company_facts_edgar_resource_kind_override(
        self,
    ) -> None:
        """edgar_resource_kind を明示指定するとその値が使われる"""
        datetime_now = datetime.now()
        f = EDGARCompanyFactsFiling(
            id="facts_kind_override",
            source="EDGAR",
            checksum="c" * 64,
            name="x.json",
            is_zip=False,
            format="json",
            created_at=datetime_now,
            edgar_resource_kind="custom_kind",
            cik="0001652044",
            filer_name="Alphabet Inc.",
            sic="7370",
            sic_description="Services",
            filer_category="Large accelerated filer",
            state_of_incorporation="DE",
            fiscal_year_end="12-31",
            tickers_key="GOOGL",
            exchanges_key="Nasdaq",
        )
        assert f.edgar_resource_kind == "custom_kind"
