# Filing APIs

The **Filing** boundary provides the document model and the query DSL. It does not depend on Collection, Catalog, or Storage.

## Public classes

| Type                           | Description                                                                                                    |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| [Filing](./Filing)             | Document model with core fields (id, source, checksum, name, is_zip, format, created_at) and extensible schema |
| [Field](./Field)               | Descriptor and query DSL (e.g. `Field("source") == "EDGAR"`)                                                   |
| [Expr](./Expr)                 | WHERE abstraction (sql + params); supports `&`, `                                                              |
| [EDINETFiling](./EDINETFiling) | Built-in subclass for EDINET documents                                                                         |
| [EDGARFiling](./EDGARFiling)   | Built-in subclass for EDGAR documents                                                                          |
