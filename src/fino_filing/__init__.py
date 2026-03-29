from .collection.catalog import Catalog
from .collection.collection import Collection
from .collection.filing_resolver import (
    FilingResolver,
    default_resolver,
    register_filing_class,
)
from .collection.storage import Storage
from .collection.storages import LocalStorage
from .collector.base import BaseCollector, Parsed, RawDocument
from .collector.edger import (
    EdgerBulkCollector,
    EdgerClient,
    EdgerConfig,
    EdgerDocumentsCollector,
    EdgerFactsCollector,
)
from .collector.edinet import EdinetCollector, EdinetConfig
from .filing.expr import Expr
from .filing.field import Field
from .filing.filing import Filing
from .filing.filing_edger import EDGARCompanyFactsFiling, EDGARFiling
from .filing.filing_edinet import EDINETFiling

# 組み込み Filing サブクラスを default_resolver に明示登録
default_resolver.register(EDINETFiling)
default_resolver.register(EDGARFiling)
default_resolver.register(EDGARCompanyFactsFiling)

__all__ = [
    "BaseCollector",
    "Catalog",
    "Collection",
    "EDGARCompanyFactsFiling",
    "EDGARFiling",
    "EDINETFiling",
    "EdgerBulkCollector",
    "EdgerClient",
    "EdgerConfig",
    "EdgerDocumentsCollector",
    "EdgerFactsCollector",
    "EdinetCollector",
    "EdinetConfig",
    "Expr",
    "Field",
    "Filing",
    "FilingResolver",
    "LocalStorage",
    "Parsed",
    "RawDocument",
    "default_resolver",
    "register_filing_class",
    "Storage",
]
