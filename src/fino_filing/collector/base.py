from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterator, Sequence

from fino_filing.collection.collection import Collection
from fino_filing.filing.filing import Filing

logger = logging.getLogger(__name__)

Meta = dict[str, Any]


@dataclass(frozen=True)
class RawDocument:
    """
    Raw Filing Properties containing content bytes and meta informations

    - content: bytes file content
    - meta: filing metadata
    """

    content: bytes
    meta: Meta


# Intermediate structure before building a Filing.
# Core fields + source-specific fields.
Parsed = dict[str, Any]


class BaseCollector(ABC):
    """
    Collector Base Class
    (Template Method)

    Implements the Template Method pattern for the collect flow and orchestrates the collect process.
    Subclasses must implement the following abstract methods:
    - _fetch_documents
    - _parse_response
    - _build_filing
    """

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def iter_collect(self, **criteria: Any) -> Iterator[tuple[Filing, str]]:
        """
        Iterates over the Filing collect flow

        Args:
            **criteria: Criteria for the collect flow. Subclasses should explicitly define the accepted criteria.
                (e.g. cik_list, limit_per_company, date_from, etc.)
        """

        for raw in self._fetch_documents(**criteria):
            parsed = self._parse_response(raw)
            filing = self._build_filing(parsed, raw.content)
            yield self._add_to_collection(filing, raw.content)

    def collect(self, **criteria: Any) -> Sequence[tuple[Filing, str]]:
        """
        Executes the collect flow and returns a sequence of tuples containing the Filing and the path.
        Wraps the iter_collect method to return batched results.

        Args:
            **criteria: Criteria for the collect flow. Subclasses should explicitly define the accepted criteria.
                (e.g. cik_list, limit_per_company, date_from, etc.)
        """
        return list(self.iter_collect(**criteria))

    @abstractmethod
    def _fetch_documents(self, **kwargs: Any) -> Iterator[RawDocument]:
        """Yields one RawDocument per fetched document."""
        ...

    @abstractmethod
    def _parse_response(self, raw: RawDocument) -> Parsed:
        """Parses the raw document and converts it to a Parsed dictionary."""
        ...

    @abstractmethod
    def _build_filing(self, parsed: Parsed, content: bytes) -> Filing:
        """Builds a Filing from the parsed data and raw content."""
        ...

    def _add_to_collection(self, filing: Filing, content: bytes) -> tuple[Filing, str]:
        """Adds a single Filing to the Collection."""
        return self._collection.add(filing, content)
