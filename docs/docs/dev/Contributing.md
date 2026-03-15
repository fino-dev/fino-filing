---
sidebar_position: 4
title: Contributing
---

# Contributing

Rules and workflows for contributing to fino-filing. See also **AGENTS.md** in the repository root (authority order: AGENTS.md → docs → user input).

## Development environment

### Lint / format on push

Auto lint and formatter will executed when you push to github repository and it will block your pushes.
If you blocked pushes, you need to fix the problem and commit them and retry it.

**Initial Development environment setup**

```bash
uv sync --group dev
uv run pre-commit install --hook-type pre-push
```

- `.pre-commit-config.yaml` execute `ruff check` and `ruff format --check`
- Hooks not executed in commit but push

**Check the executed process in manually**

```bash
uv run pre-commit run --hook-type pre-push --all-files
```

**Linter & Formatter**

```bash
uv run ruff check --fix
uv run ruff format
```

## Coding rules

### Type hints

- **Required** for all functions and methods.
- Public API must be strictly typed.

### Logging

- Use the `logging` module. **No `print`**.
- Define the logger per module:

```python
import logging
logger = logging.getLogger(__name__)
```

### Class design

- Each class must have a **comment that states its responsibility**.
- Public methods must have a **short docstring** (parameters/return value can be omitted in the docstring if clear from types).

### Public API

- Most classes are internal. Only what is listed in **`src/fino_filing/__init__.py`** under `__all__` is part of the public API.
- Do **not** change the public API without approval.

## Testing

- **pytest** is the test runner (`testpaths = ["test"]` in `pyproject.toml`).
- New use cases must have corresponding tests. Adapters may be covered by integration-style tests.

### Run tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/fino_filing --cov-report=term-missing

# One layer
pytest test/module/collection/ -v
pytest test/module/filing/ -v
pytest test/module/collector/ -v
```

### Test structure

- **`test/module/`** — By layer: collection, filing, collector, core. One test class per subject; docstrings for focus (happy path / failure / boundary).
- **`test/scenario/`** — End-to-end flows.
- Exception behavior should align with [Spec: Exception spec](/docs/spec/API/Exceptions/exception-spec).

## Development flow (agent-driven)

1. **Design** — Clarify in writing (docs or tasks under `.tasks/`).
2. **Implement** — Code (per class or use case).
3. **Test** — Add or update tests.

## Adding features

- **New Filing subclass**: Define the class with `Field`/`Annotated`, then call `default_resolver.register(YourFiling)` or use `register_filing_class(YourFiling)`. Add tests for init, to_dict/from_dict, and Catalog roundtrip if used.
- **New Collector**: Subclass `BaseCollector`, implement `fetch_documents`, `parse_response`, `build_filing`. Use existing or new Strategy classes for fetch/parse; call `add_to_collection` (which uses `Collection.add`). Add tests under `test/module/collector/`.
- **New Storage backend**: Implement the `Storage` protocol (e.g. under `collection/storages/`). Add integration tests that use Collection with that storage.
