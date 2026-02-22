# # - 正常系: findでも保存時の具象クラスで返る

#     def test_find_returns_edinet_filing_when_saved_as_edinet(
#         self,
#         temp_storage: LocalStorage,
#         temp_catalog: Catalog,
#         datetime_now: datetime,
#     ) -> None:
#         """EDINETFilingでaddした場合、findでEDINETFilingとして復元される"""
#         content = b"test content"
#         checksum = hashlib.sha256(content).hexdigest()
#         edinet_filing = EDINETFiling(
#             id="test_id_edinet_find",
#             checksum=checksum,
#             name="test_filing.txt",
#             is_zip=False,
#             created_at=datetime_now,
#             edinet_code="test_edinet_code",
#             sec_code="test_sec_code",
#             jcn="test_jcn",
#             filer_name="test_filer_name",
#             ordinance_code="test_ordinance_code",
#             form_code="test_form_code",
#             doc_type_code="test_doc_type_code",
#             doc_description="test_doc_description",
#             period_start=datetime_now,
#             period_end=datetime_now,
#             submit_datetime=datetime_now,
#         )
#         collection = Collection(storage=temp_storage, catalog=temp_catalog)
#         collection.add(edinet_filing, content)

#         results = collection.find(limit=10)
#         assert len(results) >= 1
#         filing = next(f for f in results if f.id == edinet_filing.id)
#         assert isinstance(filing, EDINETFiling)
#         assert filing.edinet_code == edinet_filing.edinet_code
#         assert filing.filer_name == edinet_filing.filer_name
