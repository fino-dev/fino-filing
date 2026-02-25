import hashlib
from datetime import datetime
from typing import Annotated

import pytest

from fino_filing import Catalog, Collection, EDINETFiling, Field, Filing
from fino_filing.collection.error import CollectionChecksumMismatchError
from fino_filing.collection.storages import LocalStorage


class TestCollection_Add:
    """
    Collection.add(). 観点: 正常系、異常系（checksum 不一致）、契約（同一 id は上書き許容）
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

        assert temp_catalog.get(filing.id) is not None
        assert temp_catalog.get(saved_filing.id) is not None

        with open(path, "rb") as f:
            actual_content = f.read()
        assert actual_content == content

        # Locator により storage_key が使われ、形式に応じた拡張子で保存される
        assert path.endswith(".xbrl")  # sample_filing is is_zip=False
        assert "test_source" in path and "test_id_001" in path

    def test_add_uses_locator_storage_key_zip_extension(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """is_zip=True の Filing は .zip 拡張子で保存される（Locator の storage_key が使われる）"""
        content = b"zip content"
        checksum = hashlib.sha256(content).hexdigest()
        filing = Filing(
            id="zip_id_001",
            source="edinet",
            checksum=checksum,
            name="report.zip",
            is_zip=True,
            format="zip",
            created_at=datetime_now,
        )
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        _, path = collection.add(filing, content)
        assert path.endswith(".zip")
        assert "edinet" in path and "zip_id_001" in path
        with open(path, "rb") as f:
            assert f.read() == content

    def test_add_uses_format_extension_pdf(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """format=pdf の Filing は .pdf 拡張子で保存され、get_content で読める"""
        content = b"pdf binary content"
        checksum = hashlib.sha256(content).hexdigest()
        filing = Filing(
            id="pdf_id_001",
            source="edinet",
            checksum=checksum,
            name="report.pdf",
            is_zip=False,
            format="pdf",
            created_at=datetime_now,
        )
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        _, path = collection.add(filing, content)
        assert path.endswith(".pdf")
        assert "edinet" in path and "pdf_id_001" in path
        loaded = collection.get_content(filing.id)
        assert loaded == content

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
            format=filing.format,
            created_at=filing.created_at,
            extra="extra",
        )

        saved_filing, path = collection.add(extended, content)

        assert temp_catalog.get(extended.id) is not None
        assert temp_catalog.get(saved_filing.id) is not None

        with open(path, "rb") as f:
            actual_content = f.read()
        assert actual_content == content

        # 保存時のインスタンスとして格納されていることを確認
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
            format="xbrl",
            created_at=datetime_now,
            doc_id="test_doc_id",
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

        assert temp_catalog.get(edinet_filing.id) is not None
        assert temp_catalog.get(saved_filing.id) is not None

        assert saved_filing.id == edinet_filing.id
        assert saved_filing.checksum == edinet_filing.checksum
        assert saved_filing.name == edinet_filing.name
        assert saved_filing.source == edinet_filing.source
        assert saved_filing.is_zip == edinet_filing.is_zip
        assert saved_filing.created_at == edinet_filing.created_at

        assert isinstance(saved_filing, EDINETFiling)
        assert saved_filing.doc_id == edinet_filing.doc_id
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

    def test_add_raises_checksum_mismatch(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """仕様: content の SHA256 が filing.checksum と不一致のとき CollectionChecksumMismatchError。検証: 例外型と filing_id, actual/expected checksum"""
        content = b"actual content"
        wrong_checksum = "0" * 64  # filing には別の checksum を渡す
        filing = Filing(
            id="checksum_test_id",
            source="test",
            checksum=wrong_checksum,
            name="x.xbrl",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        with pytest.raises(CollectionChecksumMismatchError) as e:
            collection.add(filing, content)
        assert e.value.filing_id == "checksum_test_id"
        assert e.value.expected_checksum == wrong_checksum
        assert e.value.actual_checksum == hashlib.sha256(content).hexdigest()

    def test_add_same_id_overwrites_storage(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """仕様: 同一 id で既に add 済みのときは上書き許容。catalog はスキップ、storage は上書き。検証: 2回目 add 後 get_content が新しい内容を返す"""
        content1 = b"first content"
        content2 = b"second content"
        checksum1 = hashlib.sha256(content1).hexdigest()
        checksum2 = hashlib.sha256(content2).hexdigest()
        filing1 = Filing(
            id="same_id",
            source="test",
            checksum=checksum1,
            name="a.xbrl",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        filing2 = Filing(
            id="same_id",
            source="test",
            checksum=checksum2,
            name="b.xbrl",
            is_zip=False,
            format="xbrl",
            created_at=datetime_now,
        )
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        collection.add(filing1, content1)
        collection.add(filing2, content2)
        assert collection.get_content("same_id") == content2
