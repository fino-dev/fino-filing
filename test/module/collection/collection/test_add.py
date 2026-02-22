import hashlib
from datetime import datetime
from typing import Annotated

from fino_filing import Catalog, Collection, EDINETFiling, Field, Filing, LocalStorage


class TestCollection_Add:
    """
    Collectionのadd()メソッドをテストする。
    - 正常系: Filingとcontentを追加できる
    - 正常系: 継承したFilingでも追加できる
    - 正常系: 継承したFilingでも追加できる (EDINETFiling)
    """

    def test_add_filing_and_content_success(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
    ) -> None:
        """Filingとcontentを追加できる"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        filing, content = sample_filing
        saved_filing, path = collection.add(filing, content)

        assert temp_storage.exists(filing.id)
        assert temp_storage.exists(saved_filing.id)

        with open(path, "rb") as f:
            actual_content = f.read()
        assert actual_content == content

    def test_add_filing_and_content_success_with_inheritance(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
    ) -> None:
        """継承したFilingでも追加できる"""

        class ExtendedFiling(Filing):
            extra: Annotated[str, Field(description="Extra")] = ""

        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        filing, content = sample_filing
        extended = ExtendedFiling(
            id=filing.id,
            source=filing.source,
            checksum=filing.checksum,
            name=filing.name,
            is_zip=filing.is_zip,
            created_at=filing.created_at,
            extra="extra",
        )

        saved_filing, path = collection.add(extended, content)

        assert temp_storage.exists(extended.id)
        assert temp_storage.exists(saved_filing.id)

        with open(path, "rb") as f:
            actual_content = f.read()
        assert actual_content == content

        assert isinstance(saved_filing, ExtendedFiling)
        assert saved_filing.get("extra") == "extra"

    def test_add_filing_and_content_success_with_inheritance_edinet(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
        datetime_now: datetime,
    ) -> None:
        """継承したFilingでも追加できる (EDINETFiling)"""
        content = b"test content"
        checksum = hashlib.sha256(content).hexdigest()
        edinet_filing = EDINETFiling(
            id="test_id_001",
            checksum=checksum,
            name="test_filing.txt",
            is_zip=False,
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
        )
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        saved_filing, path = collection.add(edinet_filing, content)

        assert temp_storage.exists(edinet_filing.id)
        assert temp_storage.exists(saved_filing.id)

        assert saved_filing.id == edinet_filing.id
        assert saved_filing.checksum == edinet_filing.checksum
        assert saved_filing.name == edinet_filing.name
        assert saved_filing.source == edinet_filing.source
        assert saved_filing.is_zip == edinet_filing.is_zip
        assert saved_filing.created_at == edinet_filing.created_at

        assert isinstance(saved_filing, EDINETFiling)
        assert saved_filing.edinet_code == edinet_filing.edinet_code
        assert saved_filing.sec_code == edinet_filing.sec_code
        assert saved_filing.jcn == edinet_filing.jcn
        assert saved_filing.filer_name == edinet_filing.filer_name
        assert saved_filing.ordinance_code == edinet_filing.ordinance_code
        assert saved_filing.form_code == edinet_filing.form_code
        assert saved_filing.doc_type_code == edinet_filing.doc_type_code
        assert saved_filing.doc_description == edinet_filing.doc_description
        assert saved_filing.period_start == edinet_filing.period_start
        assert saved_filing.period_end == edinet_filing.period_end
        assert saved_filing.submit_datetime == edinet_filing.submit_datetime
        assert saved_filing.parent_doc_id == edinet_filing.parent_doc_id

        with open(path, "rb") as f:
            actual_content = f.read()
        assert actual_content == content
