from typing import Any, Callable


class Row:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    def __repr__(self) -> str:
        return f"Row(data={self.data})"

    def get_value(self, column_name: str) -> Any:
        return self.data.get(column_name)

    def set_value(self, column_name: str, value: Any) -> None:
        self.data[column_name] = value

    def update_value(self, column_name: str, value: Any) -> None:
        if column_name not in self.data:
            raise KeyError(f"Column {column_name} does not exist in the row")
        self.data[column_name] = value

    def delete_column(self, column_name: str) -> None:
        if column_name not in self.data:
            raise KeyError(f"Column {column_name} does not exist in the row")
        del self.data[column_name]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Row):
            return False
        return self.data == other.data


class Column:
    def __init__(self, name: str, col_type: str) -> None:
        self.name = name
        self.col_type = col_type

    def __repr__(self) -> str:
        return f"Column(name={self.name}, type={self.col_type})"


# Abstract class for tables
class AbstractTable:
    def __init__(self, name: str, columns: list[Column]) -> None:
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.rows: list[Row] = []

    def has_column(self, column_name: str) -> bool:
        return column_name in self.columns

    def add_row(self, row: Row) -> None:
        for column_name in row.data.keys():
            if column_name not in self.columns:
                raise KeyError(
                    f"Column {column_name} does not exist in table {self.name}"
                )
        self.rows.append(row)

    def delete_column(self, column_name: str) -> None:
        if column_name not in self.columns:
            raise KeyError(f"Column {column_name} does not exist in table {self.name}")
        del self.columns[column_name]
        for row in self.rows:
            row.delete_column(column_name)

    def delete_rows(self, rows: list[Row]) -> None:
        for row in rows:
            if row in self.rows:
                self.rows.remove(row)

    def where(self, condition: Callable[[Row], bool]) -> "QueryResult":
        """
        Filters rows in the table based on the given condition and returns a new Tbl object.

        Args:
            condition (Callable[[Row], bool]): A function that takes a Row and returns True if the row matches the condition.

        Returns:
            Tbl: A new Tbl object containing the filtered rows.
        """
        filtered_rows = [row for row in self.rows if condition(row)]
        new_table = QueryResult(
            name=self.name, columns=list(self.columns.values()), rows=filtered_rows
        )
        return new_table

    def __repr__(self) -> str:
        return f"AbstractTable(name={self.name}, columns={list(self.columns.keys())}, rows={len(self.rows)})"


# Base class for tables
class Table(AbstractTable):
    pass


class QueryResult(AbstractTable):
    def __init__(self, name: str, columns: list[Column], rows: list[Row]) -> None:
        super().__init__(name, columns)
        self.rows = rows.copy()

    def __repr__(self) -> str:
        return f"QueryResult(name={self.name}, rows={len(self.rows)})"


class Schema:
    tables: dict[str, Table]

    def __init__(self) -> None:
        self.tables = {}

    def add_table(self, table: Table) -> None:
        self.tables[table.name] = table

    def has_table(self, table_name: str) -> bool:
        return table_name in self.tables

    def get_table(self, table_name: str) -> Table | None:
        return self.tables.get(table_name)

    def __repr__(self) -> str:
        return f"Schema(tables={list(self.tables.keys())})"
