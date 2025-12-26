from typing import Any, Callable, Iterable


class Value:
    pass


class Operation:
    def __init__(self, operation: str) -> None:
        self.operation = operation

    def resolve(self, left: Value, right: Value | None) -> Value:
        operation = self._operation()
        return operation(left, right)

    def _operation(self) -> Callable[[Value, Value | None], Value]:
        try:
            if self.operation == "+":
                return lambda l, r: l + r  # type: ignore
            elif self.operation == "-":
                return lambda l, r: l - r  # type: ignore
            elif self.operation == "*":
                return lambda l, r: l * r  # type: ignore
            elif self.operation == "/":
                return lambda l, r: l / r  # type: ignore
            elif self.operation == "%":
                return lambda l, r: l % r  # type: ignore
            elif self.operation == "AND":
                return lambda l, r: l and r  # type: ignore
            elif self.operation == "OR":
                return lambda l, r: l or r  # type: ignore
            elif self.operation == "NOT":
                return lambda l, r: not l  # type: ignore
            elif self.operation == ">":
                return lambda l, r: l > r  # type: ignore
            elif self.operation == "<":
                return lambda l, r: l < r  # type: ignore
            elif self.operation == ">=":
                return lambda l, r: l >= r  # type: ignore
            elif self.operation == "<=":
                return lambda l, r: l <= r  # type: ignore
            elif self.operation == "=":
                return lambda l, r: l == r  # type: ignore
            elif self.operation == "!=" or self.operation == "<>":
                return lambda l, r: l != r  # type: ignore
            else:
                raise ValueError(f"Unsupported operation: {self.operation}")
        except Exception as e:
            raise ValueError(f"Illegal operation: {self.operation}") from e


class Literal(Value):
    def __init__(self, name: str, value: Any) -> None:
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"Literal(name={self.name}, value={self.value})"


class Row(Value):
    """A representation of a row in a table."""

    def __init__(self, row: tuple[Any]) -> None:
        self.row = row

    def add_value(self, value: Any) -> None:
        self.row += (value,)


class Expression(Value):
    def __init__(self, left: Value, operation: Operation, right: Value | None) -> None:
        self.left = left
        self.operation = operation
        self.right = right

    def resolve(self) -> Value:
        left = self.left.resolve() if isinstance(self.left, Expression) else self.left
        right = (
            self.right.resolve() if isinstance(self.right, Expression) else self.right
        )

        return self.operation.resolve(left, right)


class Column:
    """
    Representation of a column in a table.
    """

    def __init__(self, name: str, col_type: str) -> None:
        self.name = name
        self.col_type = col_type

    def __repr__(self) -> str:
        return f"Column(name={self.name}, type={self.col_type})"


class Scehma:
    def __init__(self, columns: Iterable[Column]) -> None:
        self.columns = tuple(columns)
        self.index: dict[str, int] = {
            col.name: idx for idx, col in enumerate(self.columns)
        }

    def add_column(self, column: Column) -> None:
        self.columns += (column,)

    def remove_column(self, column_name: str) -> None:
        self.columns = tuple(col for col in self.columns if col.name != column_name)

    def __repr__(self) -> str:
        return f"Scehma(columns={[col.name for col in self.columns]})"

    def project(self, column_names: list[str]) -> "Scehma":
        """Returns a new schema for a given list of column names"""
        projected_columns = [col for col in self.columns if col.name in column_names]
        return Scehma(projected_columns)


class Table:
    def __init__(self, name: str, schema: Scehma) -> None:
        self.name = name
        self.columns = schema.columns
        self.rows: tuple[Row, ...] = ()

    def __getitem__(self, row_ident: str | int) -> Row:
        if isinstance(row_ident, int):
            if row_ident < 0 or row_ident >= len(self.rows):
                raise IndexError(f"Row index {row_ident} out of range")
            return self.rows[row_ident]
        else:
            raise TypeError("Row identifier must be an integer index")

    def delete_row_by_index(self, index: int) -> None:
        if index < 0 or index >= len(self.rows):
            raise IndexError(f"Row index {index} out of range")
        self.rows = self.rows[:index] + self.rows[index + 1 :]

    def project(self, column_names: list[str]) -> "Table":
        """Returns a new table projected to the given column names"""

        if not all(
            col_name in [col.name for col in self.columns] for col_name in column_names
        ):
            raise ValueError(
                "One or more column names do not exist in the table schema"
            )

        projected_schema = Scehma(
            [col for col in self.columns if col.name in column_names]
        )
        projected_table = Table(self.name, projected_schema)

        projected_rows = list[Row]()
        for row in self.rows:
            projected_values = tuple(
                row.row[projected_schema.index[col_name]] for col_name in column_names
            )
            projected_rows.append(Row(projected_values))

        projected_table.rows = tuple(projected_rows)
        return projected_table

    def filter(self, condition: Expression) -> "Table":
        """Returns a new table filtered by the given condition"""

        filtered_table = Table(self.name, Scehma(self.columns))

        filtered_rows = list[Row]()
        for row in self.rows:
            context = {col.name: row.row[idx] for idx, col in enumerate(self.columns)}

            # Evaluate the condition
            if self.evaluate_condition(condition, context):
                filtered_rows.append(row)

        filtered_table.rows = tuple(filtered_rows)
        return filtered_table


class Database:
    def __init__(self, name: str) -> None:
        self.name = name
        self.tables: dict[str, Table] = {}

    def add_table(self, table: Table) -> None:
        self.tables[table.name] = table

    def get_table(self, name: str) -> Table | None:
        return self.tables.get(name)
