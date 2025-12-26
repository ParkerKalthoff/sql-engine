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

    def __init__(self, row: tuple[Any, ...]) -> None:
        self.row = row

    def add_value(self, value: Any) -> None:
        self.row = self.row + (value,)


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


class Column(Value):
    """
    Representation of a column in a table.
    """

    SUPPORTED_TYPES = ("INT", "STR", "FLOAT", "BOOL")

    def __init__(self, name: str, col_type: str) -> None:
        if col_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported column type: {col_type}")
        self.name = name
        self.col_type: str = col_type

    def __repr__(self) -> str:
        return f"Column(name={self.name}, type={self.col_type})"


class Scehma:
    def __init__(self, columns: Iterable[Column]) -> None:
        self.columns = tuple(columns)
        self.index: dict[str, int] = {
            col.name: idx for idx, col in enumerate(self.columns)
        }

    def add_column(self, column: Column) -> None:
        if column.name in self.index:
            raise ValueError(f"Column '{column.name}' already exists in schema")

        self.columns += (column,)
        self.index[column.name] = len(self.columns) - 1

    def remove_column(self, column_name: str) -> None:
        self.columns = tuple(col for col in self.columns if col.name != column_name)
        self.index = {col.name: idx for idx, col in enumerate(self.columns)}

    def __repr__(self) -> str:
        return f"Scehma(columns={[col.name for col in self.columns]})"

    def project(self, column_names: list[str]) -> "Scehma":
        """Returns a new schema for a given list of column names"""
        projected_columns = [col for col in self.columns if col.name in column_names]
        return Scehma(projected_columns)


class Condition:
    """
    Represents a condition for filtering rows in a table.
    """

    def __init__(self, left: Value, operation: str, right: Value) -> None:
        self.left = left
        self.operation = Operation(operation)
        self.right = right

    def evaluate(self, row: Row, schema: Scehma) -> bool:
        """
        Evaluates the condition against a row using the schema.
        """

        if isinstance(self.left, Column):
            column_index = schema.index.get(self.left.name)
            if column_index is None:
                raise ValueError(
                    f"Column '{self.left.name}' does not exist in the schema"
                )
            left_row_value = row.row[column_index]
        elif isinstance(self.left, Literal):
            left_row_value = self.left.value
        elif isinstance(self.left, Expression):
            left_row_value = self.left.resolve()
        else:
            raise TypeError("Left operand must be a Column, Literal, or Expression")

        if isinstance(self.right, Column):
            column_index = schema.index.get(self.right.name)
            if column_index is None:
                raise ValueError(
                    f"Column '{self.right.name}' does not exist in the schema"
                )
            right_row_value = row.row[column_index]
        elif isinstance(self.right, Literal):
            right_row_value = self.right.value
        elif isinstance(self.right, Expression):
            right_row_value = self.right.resolve()
        else:
            raise TypeError("Right operand must be a Column, Literal, or Expression")

        result = self.operation.resolve(left_row_value, right_row_value)

        assert isinstance(result, bool), (
            "Condition evaluation must return a boolean value"
        )

        return result


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

    def add_row(self, row: Row) -> None:
        if len(row.row) != len(self.columns):
            raise ValueError("Row length does not match table schema length")

        self.rows = self.rows + (row,)

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

    def filter(self, conditions: list[Condition]) -> "Table":
        """
        Filters the table based on a list of conditions and returns a new table.
        """
        filtered_table = Table(self.name, Scehma(self.columns))

        filtered_rows: list[Row] = []
        for row in self.rows:
            if all(
                condition.evaluate(row, Scehma(self.columns))
                for condition in conditions
            ):
                filtered_rows.append(row)

        filtered_table.rows = tuple(filtered_rows)
        return filtered_table

    def count_rows(self) -> int:
        """Equivalent to COUNT(*)"""
        return len(self.rows)

    def __repr__(self) -> str:
        return f"Table(name={self.name}, columns={[col.name for col in self.columns]}, rows={len(self.rows)})"

    def print_rows(self, limit: int | None = 200) -> None:
        rows_to_print = self.rows if limit is None else self.rows[:limit]
        for row in rows_to_print:
            print(row.row)


class Database:
    def __init__(self, name: str) -> None:
        self.name = name
        self.tables: dict[str, Table] = {}

    def add_table(self, table: Table) -> None:
        self.tables[table.name] = table

    def get_table(self, name: str) -> Table | None:
        return self.tables.get(name)
