# Filing APIs

The **Filing** boundary provides the document model and the query DSL. It does not depend on Collection, Catalog, or Storage.

## Public classes

| Type                           | Description                                                                                                    |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| [Filing](/docs/spec/api/Filings/Filing)             | Document model with core fields (id, source, checksum, name, is_zip, format, created_at) and extensible schema |
| [Field](/docs/spec/api/Filings/Field)               | Descriptor and query DSL (e.g. `Field("source") == "Edgar"`)                                                   |
| [Expr](/docs/spec/api/Filings/Expr)                 | WHERE abstraction (sql + params); supports `&`, `|`, `~`                                                     |
| [EDINETFiling](/docs/spec/api/Filings/EDINETFiling) | Built-in subclass for EDINET documents                                                                         |
| [EdgarFiling](/docs/spec/api/Filings/EdgarFiling)   | Built-in subclass for one Edgar submission document (Submissions + Archives)                                  |
| [EdgarCompanyFactsFiling](/docs/spec/api/Filings/EdgarCompanyFactsFiling) | Built-in subclass for Company Facts API JSON snapshot                                                         |
