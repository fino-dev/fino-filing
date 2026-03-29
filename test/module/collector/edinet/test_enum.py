import pytest

from fino_filing.collector.edinet.enum import (
    EDINET_DOCUMENT_DOWNLOAD_TYPE,
    EDINET_DOCUMENT_LIST_TYPE,
)


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edinet
class TestEdinetEnum:
    def test_edinet_document_list_type_value(self) -> None:
        assert EDINET_DOCUMENT_LIST_TYPE.METADATA.value == 1
        assert EDINET_DOCUMENT_LIST_TYPE.METADATA_AND_LIST.value == 2

    def test_edinet_document_download_type_value(self) -> None:
        assert EDINET_DOCUMENT_DOWNLOAD_TYPE.XBRL.value == 1
        assert EDINET_DOCUMENT_DOWNLOAD_TYPE.PDF.value == 2
        assert (
            EDINET_DOCUMENT_DOWNLOAD_TYPE.ALTERNATIVE_DOCUMENTS__ATTACHMENTS.value == 3
        )
        assert EDINET_DOCUMENT_DOWNLOAD_TYPE.ENGLISH_VERSION_FILE.value == 4
        assert EDINET_DOCUMENT_DOWNLOAD_TYPE.CSV.value == 5
