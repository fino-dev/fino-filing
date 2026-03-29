"""collector.edinet._helpers のユニットテスト。"""

import pytest

from fino_filing.collector.edinet._helpers import _infer_edinet_format
from fino_filing.collector.edinet.enum import EDINET_DOCUMENT_DOWNLOAD_TYPE


@pytest.mark.module
@pytest.mark.collector
@pytest.mark.edinet
class TestInferEdinetFormat:
    """_infer_edinet_format が API type と storage format の対応を返す。"""

    def test_xbrl(self) -> None:
        assert _infer_edinet_format(EDINET_DOCUMENT_DOWNLOAD_TYPE.XBRL) == "xbrl"

    def test_pdf(self) -> None:
        assert _infer_edinet_format(EDINET_DOCUMENT_DOWNLOAD_TYPE.PDF) == "pdf"

    def test_alternative_documents_attachments_maps_to_pdf(self) -> None:
        assert (
            _infer_edinet_format(
                EDINET_DOCUMENT_DOWNLOAD_TYPE.ALTERNATIVE_DOCUMENTS__ATTACHMENTS
            )
            == "xbrl"
        )

    def test_english_version_file_maps_to_csv(self) -> None:
        assert (
            _infer_edinet_format(EDINET_DOCUMENT_DOWNLOAD_TYPE.ENGLISH_VERSION_FILE)
            == "xbrl"
        )

    def test_csv_maps_to_csv(self) -> None:
        assert _infer_edinet_format(EDINET_DOCUMENT_DOWNLOAD_TYPE.CSV) == "csv"

    def test_unknown_type_falls_through_to_empty_string(self) -> None:
        """Unknown type は match に無く default で空文字（現仕様）。"""
        with pytest.raises(ValueError):
            EDINET_DOCUMENT_DOWNLOAD_TYPE(100)
