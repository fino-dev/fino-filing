---
sidebar_position: 3
---

# Exception (Error)

Summary of conditions that lead to which exception or return value. Tests align with this list.

## Filing / Field (metaclass, init, set)

| Condition                                            | Result                                                                           | Notes |
| ---------------------------------------------------- | -------------------------------------------------------------------------------- | ----- |
| Required fields (id, source, checksum, etc.) missing | `FilingRequiredError`; `errors` / `fields` contain what is missing               |       |
| Explicit `None` for a required field                 | `FilingRequiredError`                                                            |       |
| Value with wrong type for a field                    | `FieldValidationError`; includes `field`, `expected_type`, `actual_type`         |       |
| Change an immutable field after init                 | `FieldImmutableError`; includes `field`, `current_value`, `attempt_value`        |       |
| Multiple field validation errors                     | `FilingValidationError` or `FilingImmutableError`; `errors` / `fields` list them |       |
| Fields with default may be omitted                   | OK; default used when omitted                                                    |       |
| Extended class missing required fields               | Same exceptions as above                                                         |       |

## Filing (to_dict / from_dict)

| Condition                            | Result                      | Notes |
| ------------------------------------ | --------------------------- | ----- |
| from_dict with missing required keys | `FilingRequiredError` etc.  |       |
| from_dict with wrong type            | `FieldValidationError` etc. |       |

## Collection.add

| Condition                                            | Result                                                                                            | Notes |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ----- |
| SHA256 of `content` does not match `filing.checksum` | `CollectionChecksumMismatchError`; includes `filing_id`, `actual_checksum`, `expected_checksum`   |       |
| add again with same id already added                 | **Overwrite allowed**: catalog index is skipped, storage is overwritten; returns `(filing, path)` |       |

## Collection.get_filing / get_content / get

| Condition       | Result                                                                                                      | Notes |
| --------------- | ----------------------------------------------------------------------------------------------------------- | ----- |
| Non-existent id | `get_filing`: `None`; `get_content`: `None`; `get`: `(None, None, None)` (3rd element is path: str \| None) |       |

## Locator.resolve

| Condition                           | Result                                                      | Notes |
| ----------------------------------- | ----------------------------------------------------------- | ----- |
| Filing cannot be resolved (no path) | `LocatorPathResolutionError` (raised inside Collection.add) |       |

## Exception message format

- Base: `FinoFilingException`. `message` includes the prefix `"[Fino Filing] "`.
- `FilingValidationError` / `FilingImmutableError` / `FilingRequiredError`: `str(exception)` may include `errors` as newline-separated lines (spec only guarantees that they are present; exact format is not part of the spec).

## See also

- [API Reference Overview](../intro)
- Test coverage: [test-matrix](/docs/dev/testing/test-matrix) (if present)
- Strategy: [testing-strategy](/docs/dev/testing/testing-strategy) (if present)
