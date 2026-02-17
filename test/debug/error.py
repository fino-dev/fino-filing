# raise FinoFilingException("test message")

from fino_filing.filing.error import FilingValidationError

try:
    raise FilingValidationError(
        "test message", errors=["error1", "error2"], fields=["field1", "field2"]
    )
except FilingValidationError as e:
    print(e.__str__())
