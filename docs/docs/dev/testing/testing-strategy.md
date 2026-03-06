# Test Strategy (focus, cases, tools)

## 0. Test docstring conventions

- **Test class**: State the subject under test and which focus (happy path / failure / boundary) the class mainly covers, in one line.
- **Test method (failure)**: Include “Spec: (one-line spec).” Optionally describe what is asserted (exception type, return value, attributes).
- **Test method (happy path)**: One line on what is being verified.

## 1. What tests should cover

### 1.1 Focus categories

| Focus | Meaning | Current examples |
|-------|---------|------------------|
| **Happy path** | Contract-compliant input → expected output/side effect | add/get/get_content, to_dict/from_dict, get_indexed_fields |
| **Failure** | Invalid input, missing data, wrong type → correct exception or return | FilingRequiredError, FieldValidationError, get_not_found |
| **Boundary / edge** | Empty, None, empty string, min/max, duplicates | test_none (explicit None), duplicate id TODO |
| **Contract / invariants** | Roundtrip after persist, checksum match, immutable violation | add→get roundtrip, checksum mismatch exception |
| **Public API** | Behavior of classes/functions in `__all__` | Partially covered per module; Expr, Resolver, EDGAR thin or missing |

### 1.2 Per-layer emphasis

- **Filing / Field / Meta**: Happy, failure, boundary (required/optional/immutable/default). Assert type and message where relevant.
- **Collection / Catalog**: Happy path plus not_found, checksum mismatch, duplicate id (once spec is fixed). Integration-style is fine (AGENTS.md).
- **Locator / Storage**: Extension, partition, storage_key combinations. Failure (invalid path, etc.) as needed.
- **FilingResolver**: register → resolve, None/unregistered, dynamic import success/failure.
- **Expr**: AND/OR/NOT composition and param order/content. Integration with Catalog.search.

### 1.3 Role of Collection

- **Collection is a Facade**; do not test it in isolation. Its public methods (add, get, get_filing, get_content, get_path, search) are validated in **integration tests** with real LocalStorage, Catalog, Locator.
- Delegatees (Catalog, Locator, LocalStorage) are unit-tested. Collection tests focus on “facade behavior”.

### 1.4 Scope by public contract

- Test **contractually meaningful cases** for the public API, not every implementation path.
- Use one representative per equivalence class and `@pytest.mark.parametrize` for same logic, different inputs.

---

## 2. Adding and reorganizing cases

### 2.1 Gaps to fill

- **Failure behavior**
  - `Collection.add`: duplicate add with same id (spec: overwrite or error) → pin in tests.
  - `get_content`: test path that raises `CollectionChecksumMismatchError` on checksum mismatch.
- **Under-covered modules**
  - **Expr**: Test combined result (sql/params) of `__and__` / `__or__` / `__invert__`. Integrate with `Catalog.search(expr=...)` if needed.
  - **FilingResolver**: register → resolve match, resolve(None) → None, unregistered name → dynamic resolve or None. Backward compat of `register_filing_class`.
  - **EDGARFiling**: At least one init/roundtrip similar to EDINETFiling.
  - **Catalog**: index_batch, search limit/offset/order, count, clear (at least one test per method not yet hit).
- **Commented-out scenarios**
  - test_collection.py, test_init.py search-related, test_search roundtrip type. Re-enable if spec is fixed; otherwise test “not implemented” or skip with a note.

### 2.2 Reorganization

- **One test class per subject** (class or method group). Docstring: one line on happy/failure/boundary.
- **Use parametrize**: Same logic, different I/O (e.g. exception message/attrs, formats) → `@pytest.mark.parametrize`.
- **Fixture types**: e.g. `sample_filing` return type `tuple[Filing, bytes]` (align with conftest).

---

## 3. Coverage

### 3.1 Whether to use it

- **Recommended**: Shows which code is exercised; helps find untested branches (especially failure and error handling).
- **Goal**: Don’t aim for 100% immediately. Start with **line coverage**, prioritize **public API (`__all__`)** and **error paths**.
- **Tool**: `pytest-cov`. Add to `pyproject.toml` `[tool.pytest.ini_options]` and test deps.

Example (pyproject.toml):

```toml
[tool.pytest.ini_options]
addopts = "--tb=short"
testpaths = ["test"]

[tool.coverage.run]
source = ["src/fino_filing"]
branch = true

[tool.coverage.report]
exclude_lines = ["pragma: no cover", "def __repr__", "raise NotImplementedError"]
```

- **Branch coverage**: Useful to see both sides of conditionals; line-only is fine to start.

### 3.2 Usage

- Run `pytest --cov` in CI; start with a soft threshold (e.g. 80%) and improve untested files first.

---

## 4. Mutation testing

### 4.1 Whether to use it

- **Purpose**: Check if tests detect implementation changes (mutate code, see if tests fail).
- **Recommendation**: After coverage is in place, use on **high-trust modules** (Filing validation/persist/restore, Expr composition, Resolver) to avoid long runs.
- **Tool**: e.g. `mutmut`; limit paths.

Example:

```bash
mutmut run --paths-to-mutate=src/fino_filing/filing/ --runner "pytest test/module/filing -x"
```

### 4.2 Usage

- Run manually (e.g. weekly or before PR). If a mutation survives, add a test or ignore that mutation. In CI, limit scope and set a timeout.

---

## 5. Priority

1. **Fill focus gaps**: Pin failure/boundary (duplicate id, checksum, None/unregistered) in spec and tests.
2. **Under-covered API**: At least one test each for Expr, FilingResolver, EDGARFiling, Catalog main methods.
3. **Parametrize and docstrings**: Deduplicate tests, align docstrings with focus.
4. **Coverage**: Start with pytest-cov, raise coverage on public API and error paths.
5. **Mutation**: Try on core (filing, expr, resolver); add tests from surviving mutations.

---

## 6. See also

- [test-matrix](./test-matrix): Public API × focus coverage table.
- AGENTS.md: pytest default; add tests for new use cases; adapters can be integration-style.
- [Usage scenarios](/docs/spec/scenarios): Collection usage; reference for scenario tests.
