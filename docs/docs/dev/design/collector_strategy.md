# Collector Boundary Design

## Design goals

- Fetch documents **in the right format per disclosure source** and store them in Collection
- Centralize the common flow in BaseCollector; implement specifics in EdinetCollector / EdgerCollector
- **Source-specific behavior** (Filing type, config, API) is defined and absorbed in Edinet / Edger classes
- Edger supports multiple APIs and data formats; do **not** force it into a single path like Edinet—**implement separately** per use case

---

## 1. Core idea

### Collector responsibilities

- **BaseCollector**: Template that defines the common flow (fetch → parse → build_filing → add_to_collection)
- **EdinetCollector / EdgerCollector**: Implement that flow per source and integrate with Collection

### Absorbing source-specific behavior

Source-specific differences stay inside **Edinet / Edger** classes.

- **Edinet**: Config, API, response format, and conversion to EDINETFiling for EDINET
- **EdgerSecApi / EdgerBulkData**: Config and fetch/parse per EDGAR API/format, conversion to EDGARFiling

Concrete collectors **orchestrate** these and persist via Collection.

---

## 2. Design patterns

| Pattern | Role |
|--------|------|
| **Template Method** | BaseCollector defines the skeleton of `collect()`; subclasses override `fetch_documents()`, `parse_response()`, `build_filing()` |
| **Strategy** | Edinet, EdgerSecApi, EdgerBulkData encapsulate the “fetch → parse → build Filing” strategy |
| **Facade integration** | Collector uses Collection (Facade) and only calls add; it receives a Collection instance at construction to bind to that collection |

---

## 3. Responsibility split

| Component | Responsibility |
|-----------|-----------------|
| BaseCollector | Common flow, delegating add to Collection, defining template methods |
| EdinetCollector | Orchestrating Edinet; EDINET-specific fetch/parse/build_filing |
| EdgerCollector | Orchestrating EdgerSecApi / EdgerBulkData; collection per API/format |
| Edinet | EDINET config, API, format, and to_filing → EDINETFiling |
| EdgerSecApi | SEC API fetch/parse and to_filing → EDGARFiling |
| EdgerBulkData | Bulk data fetch/parse and to_filing → EDGARFiling |
| EdinetConfig / EdgerConfig | Per-source settings (API base, timeout, etc.) |
| Collection | Single entry for storage and search (existing Facade) |

---

## 4. Edger multi-API / multi-format

Edger has more varied APIs and formats than Edinet.

- **Do not** force Edger into a single path to match Edinet
- Implement **EdgerSecApi** (SEC API, etc.) and **EdgerBulkData** (bulk data, etc.) as **separate classes per use case**
- Each class fetches, parses, and builds EDGARFiling in the form that fits it
- EdgerCollector holds these and orchestrates by switching or combining Sec / Bulk as needed

That way Edger is not constrained by Edinet’s simple one-source-one-format assumption.

---

## 5. Flow overview

```
BaseCollector.collect()
  → fetch_documents()     # implemented in concrete class (may delegate to Edinet / EdgerSecApi / EdgerBulkData)
  → parse_response(raw)   # parse per source format
  → build_filing(parsed)  # produce EDINETFiling / EDGARFiling
  → add_to_collection(filing, content)  # delegate to Collection.add
```

---

## 6. Principles

- Shared behavior in BaseCollector; source-specific in Edinet / Edger*
- Filing type, config, and API differences are defined and absorbed in Edinet / Edger classes
- Collectors only orchestrate and talk to Collection
- Edger: multiple APIs/formats as separate classes, each collecting in the shape that fits
- Keep the existing Collection / Filing boundaries

---

## See also

- Class diagram: [architecture.puml](./architecture.puml) (Collector boundary)
- Field/DSL design: [field_type_strategy.md](./field_type_strategy.md)
