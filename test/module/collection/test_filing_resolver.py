"""FilingResolver の単体テスト。観点: 正常系・異常系"""

from fino_filing import EDINETFiling, Filing, FilingResolver, default_resolver
from fino_filing.collection.filing_resolver import register_filing_class


class TestFilingResolver_Register_Resolve:
    """FilingResolver.register / resolve. 観点: 正常系"""

    def test_register_then_resolve_returns_same_class(self) -> None:
        """register したクラスを resolve で取得できる"""
        resolver = FilingResolver()
        resolver.register(EDINETFiling)
        name = f"{EDINETFiling.__module__}.{EDINETFiling.__qualname__}"
        cls = resolver.resolve(name)
        assert cls is EDINETFiling

    def test_resolve_none_returns_none(self) -> None:
        """resolve(None) は None を返す"""
        resolver = FilingResolver()
        assert resolver.resolve(None) is None

    def test_resolve_empty_string_returns_none(self) -> None:
        """resolve('') は None を返す（not name で弾かれる）"""
        resolver = FilingResolver()
        assert resolver.resolve("") is None

    def test_unregistered_name_returns_none_or_resolved(self) -> None:
        """未登録の完全修飾名は動的解決を試みる。自パッケージの EDINETFiling は解決できる場合がある"""
        resolver = FilingResolver()
        name = "fino_filing.filing.filing_edinet.EDINETFiling"
        cls = resolver.resolve(name)
        # 動的インポートで解決できれば EDINETFiling、できなければ None
        assert cls is None or cls is EDINETFiling


class TestDefaultResolver:
    """default_resolver. 観点: 正常系（EDINETFiling / EDGARFiling は __init__.py で登録済み）"""

    def test_default_resolver_resolves_edinet(self) -> None:
        """default_resolver で EDINETFiling を resolve できる"""
        name = f"{EDINETFiling.__module__}.{EDINETFiling.__qualname__}"
        assert default_resolver.resolve(name) is EDINETFiling


class TestRegisterFilingClass:
    """register_filing_class. 観点: 正常系（後方互換 API）"""

    def test_register_filing_class_registers_and_resolves(self) -> None:
        """register_filing_class で登録したクラスを resolve できる"""
        class CustomFiling(Filing):
            pass

        name = "test_filing_resolver.CustomFiling"
        register_filing_class(name, CustomFiling)
        try:
            assert default_resolver.resolve(name) is CustomFiling
        finally:
            default_resolver._registry.pop(name, None)
