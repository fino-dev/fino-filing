"""Filing の属性アクセス・get/set の振る舞い"""

from datetime import datetime

from fino_filing.filing.filing import EDINETFiling, Filing


def test_filing_attr_access_defined_fields() -> None:
    """定義済みフィールドは filing.id, filing.source 等で取得できる"""
    f = Filing(
        content=b"hello",
        id="hoge_id",
        source="test",
        name="test.zip",
        is_zip=True,
        created_at=datetime(2024, 1, 15),
    )
    assert f.id == "hoge_id"
    assert f.source == "test"
    assert f.name == "test.zip"
    assert f.is_zip is True
    assert f.created_at == datetime(2024, 1, 15)
    assert f.checksum == f.make_checksum(b"hello")


def test_filing_attr_access_undefined_key_via_set() -> None:
    """set() で入れた未定義キーは属性で取得できる（例: doc_id）"""
    f = Filing(
        content=b"",
        id="x",
        source="s",
        name="n",
        is_zip=False,
        created_at=datetime(2024, 1, 1),
    )
    f.set("doc_id", "doc-123")
    assert f.doc_id == "doc-123"


def test_filing_get() -> None:
    """get(key) で定義済み・未定義どちらのキーも取得できる"""
    f = Filing(
        content=b"",
        id="id1",
        source="src",
        name="n",
        is_zip=False,
        created_at=datetime(2024, 1, 1),
    )
    assert f.get("id") == "id1"
    assert f.get("source") == "src"
    f.set("custom", "v")
    assert f.get("custom") == "v"
    assert f.get("nonexistent", "default") == "default"


def test_filing_set_defined_field() -> None:
    """set() で定義済みフィールドを上書きできる"""
    f = Filing(
        content=b"",
        id="id1",
        source="s",
        name="n",
        is_zip=False,
        created_at=datetime(2024, 1, 1),
    )
    f.set("id", "id2")
    assert f.id == "id2"
    assert f.get("id") == "id2"


def test_edinet_filing_attr_access() -> None:
    """EDINETFiling の固有フィールドも属性で取得できる"""
    f = EDINETFiling(
        content=b"",
        id="e1",
        source="edinet",
        name="n",
        is_zip=False,
        created_at=datetime(2024, 1, 1),
        filer_name="株式会社サンプル",
        edinet_code="E12345",
    )
    assert f.id == "e1"
    assert f.filer_name == "株式会社サンプル"
    assert f.edinet_code == "E12345"
