from dataclasses import dataclass
from typing import Any, Callable, Tuple, Union


@dataclass(frozen=True)
class Row:
    row: tuple[Any, ...]

    def __getitem__(self, index: int) -> Any:
        return self.row[index]

    def get_hash(self, indices: list[int]):
        """Used to get hash for hash filtering, joins"""
        return hash(tuple(self.row[i] for i in indices))

    # Typing
    Operand = Union["Row", Tuple[Any, ...]]
    BinaryOp = Callable[[Any, Any], Any]

    # -------------------------
    # Helpers
    # -------------------------
    def _coerce(self, other: Operand) -> tuple[Any, ...]:
        if isinstance(other, Row):
            return other.row
        if isinstance(other, tuple):  # type: ignore
            return other
        raise TypeError(f"Unsupported operand type: {type(other)!r}")

    def _elementwise(self, other: Operand, op: BinaryOp) -> "Row":
        other_row = self._coerce(other)
        if len(self.row) != len(other_row):
            raise ValueError("Row lengths must match")
        return Row(tuple(op(a, b) for a, b in zip(self.row, other_row)))

    # Equality
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Row):
            return self.row == other.row
        if isinstance(other, tuple):
            return self.row == other
        return NotImplemented

    # Arithmetic (SQL: + - * / %)
    def __add__(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: a + b)

    def __sub__(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: a - b)

    def __mul__(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: a * b)

    def __truediv__(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: a / b)

    def __mod__(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: a % b)

    # Comparison (SQL: != < <= > >=)
    # Result: Row[bool]
    def __lt__(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: a < b)

    def __le__(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: a <= b)

    def __gt__(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: a > b)

    def __ge__(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: a >= b)

    def ne(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: a != b)

    # Logical (SQL: AND OR NOT)
    def __and__(self, other: Operand) -> "Row":
        return self._elementwise(other, lambda a, b: bool(a) and bool(b))

    def __or__(self, other: Operand) -> "Row":
        """SQL OR (boolean) OR concat fallback"""
        other_row = self._coerce(other)
        if all(isinstance(x, bool) for x in self.row + other_row):
            return self._elementwise(other, lambda a, b: bool(a) or bool(b))
        return Row(self.row + other_row)  # CONCAT

    def __invert__(self) -> "Row":
        """SQL NOT"""
        return Row(tuple(not bool(x) for x in self.row))

    def is_null(self) -> "Row":
        return Row(tuple(x is None for x in self.row))

    def is_not_null(self) -> "Row":
        return Row(tuple(x is not None for x in self.row))

    def coalesce(self, other: Operand) -> "Row":
        other_row = self._coerce(other)
        if len(self.row) != len(other_row):
            raise ValueError("Row lengths must match")
        return Row(
            tuple(a if a is not None else b for a, b in zip(self.row, other_row))
        )


@dataclass
class Column:
    name: str
    type: str
    default: Any = None


@dataclass
class Schema:
    columns: tuple[Column, ...]

    def add_column(self, col: Column) -> None:
        if any([column.name for column in self.columns if column.name == col.name]):
            raise SyntaxError

        self.columns = self.columns + (col,)  # type: ignore

    def get_indices(self, column_names: list[str]) -> dict[str, int]:
        indices = {
            column.name: index
            for index, column in enumerate(self.columns)
            if column.name in column_names
        }
        if not indices:
            raise SyntaxError
        return indices

    def get_index(self, column_name: str) -> int:
        try:
            return [
                index
                for index, column in enumerate(self.columns)
                if column.name == column_name
            ][0]
        except IndexError:
            raise SyntaxError

    def select_schema(self, column_names: list[str]) -> "Schema":
        columns = tuple(
            [
                Column(column.name, column.type, column.default)
                for column in self.columns
                if column.name in column_names
            ]
        )
        return Schema(columns=columns)

    def copy(self) -> "Schema":
        return Schema(columns=self.columns)


@dataclass
class Dataframe:
    schema: Schema
    rows: tuple[Row, ...]

    def __getitem__(self, value: str | list[str]) -> "Dataframe":
        if isinstance(value, str):
            value = [value]

        if isinstance(value, list):  # type: ignore
            schema = self.schema.select_schema(value)
            # use list comprehension to ensure ordering
            indices = [self.schema.get_indices(value)[column] for column in value]

            rows = tuple(Row(tuple(row[i] for i in indices)) for row in self.rows)

            return Dataframe(schema=schema, rows=rows)

        raise SyntaxError

    def add_row(self, row: Row) -> None:
        self.rows += (row,)

    # TODO Revise into something like (df['salary'] > 30000 & df['age'] == 30), where salary and age resolves to a set of ints, where the and resolves the sets into a singular list
    def filter(self, condition: bool | list[bool]) -> "Dataframe":
        schema = self.schema.copy()

        if isinstance(condition, bool):
            condition = [condition]

        rows = tuple(row for row, cond in zip(self.rows, condition) if cond)

        return Dataframe(schema=schema, rows=rows)
