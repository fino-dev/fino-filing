class Field:
    def __init__(self, name):
        self.name = name

    def _expr(self, op, value):
        return Expr(f"json_extract(metadata, '$.{self.name}') {op} ?", [value])

    def __eq__(self, v):
        return self._expr("=", v)

    def __gt__(self, v):
        return self._expr(">", v)

    def __lt__(self, v):
        return self._expr("<", v)


class Expr:
    def __init__(self, sql, params):
        self.sql = sql
        self.params = params

    def __and__(self, other):
        return Expr(f"({self.sql}) AND ({other.sql})", self.params + other.params)

    def __or__(self, other):
        return Expr(f"({self.sql}) OR ({other.sql})", self.params + other.params)
