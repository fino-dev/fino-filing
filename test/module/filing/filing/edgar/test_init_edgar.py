"""EdgarArchiveFiling の初期化テスト。観点: 正常系"""

from datetime import date, datetime

import pytest

from fino_filing import EdgarArchiveFiling, EdgarBulkFiling, EdgarCompanyFactsFiling
from fino_filing.collector.edgar.archive.enum import EdgarDocumentsFetchMode
from fino_filing.collector.edgar.bulk.enum import EdgarBulkType
from fino_filing.util.content import sha256_checksum


@pytest.mark.module
@pytest.mark.filing
@pytest.mark.edgar
class TestEdgarFiling:
    """Test Edgar Filing"""

    class TestEdgarCompanyFactsFiling:
        """Test EdgarCompanyFactsFiling"""

        def test_filing_initialize_edgar_company_facts_success(
            self, sample_content: bytes
        ) -> None:
            """EdgarCompanyFactsFiling 正常に初期化できる"""
            datetime_now = datetime.now()
            f = EdgarCompanyFactsFiling(
                id="facts_id",
                checksum=sha256_checksum(sample_content),
                name="sample_name",
                is_zip=False,
                format="json",
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
            assert f.source == "EDGAR"
            assert f.checksum == sha256_checksum(sample_content)
            assert f.name == "sample_name"
            assert f.is_zip is False
            assert f.format == "json"
            assert datetime_now <= f.created_at
            assert f.cik == "0001652044"
            assert f.filer_name == "Alphabet Inc."
            assert f.sic == "7370"
            assert f.sic_description == "Services"
            assert f.filer_category == "Large accelerated filer"
            assert f.state_of_incorporation == "DE"
            assert f.fiscal_year_end == "12-31"
            assert f.tickers_key == "GOOGL"
            assert f.exchanges_key == "Nasdaq"
            assert f.edgar_resource_kind == "companyfacts"

        def test_filing_default_name_success(self) -> None:
            """EdgarCompanyFactsFiling のデフォルト名が正常に生成される"""
            assert (
                EdgarCompanyFactsFiling.build_default_name("1652044")
                == "CIK0001652044-companyfacts.json"
            )

    class TestEdgarArchiveFiling:
        """Test EdgarArchiveFiling"""

        def test_filing_initialize_edgar_success(
            self, datetime_now: datetime, date_now: date, sample_content: bytes
        ) -> None:
            """EdgarArchiveFiling を正常に初期化できる"""
            edgar_filing = EdgarArchiveFiling(
                # filing core
                id="edgar_id",
                checksum=sha256_checksum(sample_content),
                name="sample_name",
                is_zip=False,
                format="xbrl",
                # edgar company meta
                cik="0001234567",
                entity_type="operating",
                filer_name="Test Corp",
                sic="7370",
                sic_description="Services",
                filer_category="Large accelerated filer",
                state_of_incorporation="DE",
                fiscal_year_end="12-31",
                tickers_key="GOOGL",
                exchanges_key="Nasdaq",
                # filing meta
                accession_number="0001234567-24-000001",
                filing_date=date_now,
                report_date=date_now,
                acceptance_date_time=datetime_now,
                act="10-K",
                form="10-K",
                items="5.07,9.01",
                core_type="SCHEDULE 13G/A",
                is_xbrl=True,
                is_inline_xbrl=False,
                primary_document="primary_document",
                primary_doc_description="primary_doc_description",
            )
            assert edgar_filing.id == "edgar_id"
            assert edgar_filing.source == "EDGAR"
            assert edgar_filing.checksum == sha256_checksum(sample_content)
            assert edgar_filing.name == "sample_name"
            assert edgar_filing.is_zip is False
            assert edgar_filing.format == "xbrl"
            assert datetime_now <= edgar_filing.created_at
            assert edgar_filing.cik == "0001234567"
            assert edgar_filing.entity_type == "operating"
            assert edgar_filing.filer_name == "Test Corp"
            assert edgar_filing.sic == "7370"
            assert edgar_filing.sic_description == "Services"
            assert edgar_filing.filer_category == "Large accelerated filer"
            assert edgar_filing.state_of_incorporation == "DE"
            assert edgar_filing.fiscal_year_end == "12-31"
            assert edgar_filing.tickers_key == "GOOGL"
            assert edgar_filing.exchanges_key == "Nasdaq"
            assert edgar_filing.accession_number == "0001234567-24-000001"
            assert edgar_filing.filing_date == date_now
            assert edgar_filing.report_date == date_now
            assert edgar_filing.acceptance_date_time == datetime_now
            assert edgar_filing.act == "10-K"
            assert edgar_filing.form == "10-K"
            assert edgar_filing.items == "5.07,9.01"
            assert edgar_filing.core_type == "SCHEDULE 13G/A"
            assert edgar_filing.is_xbrl is True
            assert edgar_filing.is_inline_xbrl is False
            assert edgar_filing.primary_document == "primary_document"
            assert edgar_filing.primary_doc_description == "primary_doc_description"

        def test_filing_default_name_primary_only_success(self) -> None:
            """EdgarArchiveFiling のデフォルト名が正常に生成される (PRIMARY_ONLY)"""
            assert (
                EdgarArchiveFiling.build_default_name(
                    "1234567",
                    "0001234567-24-000001",
                    EdgarDocumentsFetchMode.PRIMARY_ONLY,
                    "xbrl",
                )
                == "CIK0001234567_0001234567-24-000001_primary_xbrl"
            )

        def test_filing_default_name_full_success(self) -> None:
            """EdgarArchiveFiling のデフォルト名が正常に生成される (FULL)"""
            assert (
                EdgarArchiveFiling.build_default_name(
                    "1234567",
                    "0001234567-24-000001",
                    EdgarDocumentsFetchMode.FULL,
                    "xbrl",
                )
                == "CIK0001234567_0001234567-24-000001_full_xbrl"
            )

    class TestEdgarBulkFiling:
        """Test EdgarBulkFiling"""

        def test_filing_initialize_edgar_bulk_success(
            self, sample_content: bytes, date_now: date
        ) -> None:
            """EdgarBulkFiling を正常に初期化できる"""
            edgar_filing = EdgarBulkFiling(
                id="bulk_id",
                checksum=sha256_checksum(sample_content),
                name="sample_name",
                bulk_type=EdgarBulkType.COMPANY_FACTS.value,
                bulk_date=date_now,
            )
            assert edgar_filing.id == "bulk_id"
            assert edgar_filing.source == "EDGAR"
            assert edgar_filing.checksum == sha256_checksum(sample_content)
            assert edgar_filing.name == "sample_name"
            assert edgar_filing.is_zip is True
            assert edgar_filing.format == "json"
            assert edgar_filing.bulk_type == "companyfacts"
            assert edgar_filing.bulk_date == date_now
            assert edgar_filing.edgar_resource_kind == "bulk"

        def test_filing_default_name_success(self, date_now: date) -> None:
            """EdgarBulkFiling のデフォルト名が正常に生成される"""
            assert (
                EdgarBulkFiling.build_default_name(
                    bulk_type="companyfacts",
                    bulk_date=date_now,
                )
                == f"bulk-companyfacts-{date_now.strftime('%Y%m%d')}.zip"
            )
