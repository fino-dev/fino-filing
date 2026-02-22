import hashlib
from datetime import datetime

from fino_filing import Catalog, Collection, EDINETFiling, Filing
from fino_filing.collection.storages import LocalStorage


class TestCollection_Get:
    """
    Collectionのget()メソッドをテストする。
    - 正常系: add後にgetでFilingとcontentが取得できる
    - 正常系: EDINETFilingで保存した場合はgetでEDINETFilingとして返る
    - 正常系: 存在しないidでNoneが返る
    """

    # TODO: 既存のdbが存在する場合に既存のFilingが返る

    def test_get_filing_and_content_success(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
    ) -> None:
        """Filingとcontentが取得できる"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        filing, content = sample_filing

        # add
        saved_filing, actual_path = collection.add(filing, content)

        assert actual_path is not None
        assert isinstance(actual_path, str)
        assert isinstance(saved_filing, Filing)

        assert temp_storage.exists(filing.id)
        assert temp_storage.exists(saved_filing.id)

        # catalogに登録されていることを確認
        filing, content = collection.get(filing.id)
        assert filing is not None
        assert isinstance(filing, Filing)
        assert filing.id == saved_filing.id
        assert filing.name == saved_filing.name
        assert content is not None
        assert isinstance(content, bytes)
        assert content == b"test content"

    def test_get_filing_returns_edinet_filing_when_saved_as_edinet(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        datetime_now: datetime,
    ) -> None:
        """EDINETFilingでaddした場合、get_filingでEDINETFilingとして復元される"""
        content = b"test content"
        checksum = hashlib.sha256(content).hexdigest()
        edinet_filing = EDINETFiling(
            id="test_id_edinet",
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
        collection.add(edinet_filing, content)

        filing = collection.get_filing(edinet_filing.id)
        assert filing is not None
        assert isinstance(filing, EDINETFiling)
        assert filing.id == edinet_filing.id
        assert filing.doc_id == edinet_filing.doc_id
        assert filing.edinet_code == edinet_filing.edinet_code
        assert filing.sec_code == edinet_filing.sec_code
        assert filing.jcn == edinet_filing.jcn
        assert filing.filer_name == edinet_filing.filer_name
        assert filing.ordinance_code == edinet_filing.ordinance_code
        assert filing.form_code == edinet_filing.form_code
        assert filing.doc_type_code == edinet_filing.doc_type_code
        assert filing.doc_description == edinet_filing.doc_description
        assert filing.period_start == edinet_filing.period_start
        assert filing.period_end == edinet_filing.period_end
        assert filing.submit_datetime == edinet_filing.submit_datetime
        assert filing.parent_doc_id == edinet_filing.parent_doc_id

    def test_get_filing_and_content_not_found(
        self,
        temp_storage: LocalStorage,
        temp_catalog: Catalog,
        sample_filing: tuple[Filing, bytes],
    ) -> None:
        """存在しない場合、Noneが返る"""
        collection = Collection(storage=temp_storage, catalog=temp_catalog)
        filing, content = sample_filing
        collection.add(filing, content)

        filing, content = collection.get("nonexistent_id")
        assert filing is None
        assert content is None
