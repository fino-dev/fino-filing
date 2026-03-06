# fino-filing Design Pattern Catalog

GoF patterns that are **relevant for adoption** in fino-filing.  
“In use” = already used; “Recommended” = good to adopt.

---

## Creational

| Pattern | Status | Notes |
|---------|--------|-------|
| **Factory Method** | Recommended | `Filing.from_dict` is one. Centralizing Catalog/Storage/Collection creation in factories improves testability and extension (addresses “scattered object creation” from redesign). |
| **Abstract Factory** | Optional | Consider if we need to create “families” of storage + catalog together. Current single-injection is enough. |
| **Builder** | Recommended | Stepwise construction for Collection (“default_dir + LocalStorage + Catalog”) and client config improves usability and tests (redesign). |
| **Prototype** | Not needed | No real need to clone Filing today. |
| **Singleton** | Not needed | Library; callers own instances. |

---

## Structural

| Pattern | Status | Notes |
|---------|--------|-------|
| **Adapter** | In use | `Storage` (Protocol) and `LocalStorage`. File system behind a single interface; S3 etc. would be added as Adapters. |
| **Bridge** | Optional | Consider if we need to vary storage implementation and index (Catalog) implementation independently. |
| **Composite** | Not needed | Expr AND/OR is flat, not a tree. |
| **Decorator** | Optional | Consider for “compression”, “encryption” around storage. |
| **Facade** | In use | `Collection` is the Facade; single API: add / get / get_filing / get_content / search. |
| **Flyweight** | Not needed | Low priority for sharing Field etc. |
| **Proxy** | Optional | Consider for lazy-load or cached Storage. |

---

## Behavioral

| Pattern | Status | Notes |
|---------|--------|-------|
| **Chain of Responsibility** | Not needed | No requirement for search/save pipelines. |
| **Command** | Optional | Consider if add/clear etc. need to be Commands for undo/redo or replay. |
| **Iterator** | Optional | `search()` returns a list; consider an iterator API for large result sets. |
| **Mediator** | Not needed | Collection as Facade is enough. |
| **Memento** | Not needed | No snapshot/restore requirement. |
| **Observer** | Optional | Consider for sync progress or events. |
| **State** | Not needed | Collection state is simple. |
| **Strategy** | In use + Recommended | **In use**: `Locator` is the “Filing → path” Strategy. **Recommended**: Strategy for metadata store (Catalog implementation) for pluggability. |
| **Template Method** | In use | `FilingMeta` class analysis → Field injection; Filing subclasses follow the template. |
| **Visitor** | Not needed | No need to traverse Expr/Field in multiple ways. |

---

## Priority summary

1. **Factory Method** — Centralize creation of Catalog, Storage, default Collection; easier tests and extension.
2. **Builder** — Stepwise construction for Collection and client config; scales with more options.
3. **Strategy** — Interface for metadata store (DuckDB / others) for pluggability.
4. **Adapter** (continue) — New storage (e.g. S3) as Adapters implementing the Storage protocol.
5. **Facade** (continue) — Keep public API on Collection so internal changes have limited impact.
