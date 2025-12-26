from PQL.engine_v1.models.schema_models import Condition, Database, Literal
from PQL.engine_v1.models.schema_models import Table, Scehma, Column, Row


def test_database_creation():
    db = Database(name="test_db")
    assert db.name == "test_db"
    assert db.tables == {}


def test_add_and_get_table():
    db = Database(name="test_db")

    schema = Scehma(
        columns=[Column(name="id", col_type="INT"), Column(name="name", col_type="STR")]
    )
    table = Table(name="users", schema=schema)
    db.add_table(table)

    retrieved_table = db.get_table("users")
    assert retrieved_table is not None
    assert retrieved_table.name == "users"
    assert len(retrieved_table.columns) == 2
    assert retrieved_table.columns[0].name == "id"
    assert retrieved_table.columns[1].name == "name"

    non_existent_table = db.get_table("non_existent")
    assert non_existent_table is None


def test_table_projection():
    schema = Scehma(
        columns=[
            Column(name="id", col_type="INT"),
            Column(name="name", col_type="STR"),
            Column(name="age", col_type="INT"),
        ]
    )
    table = Table(name="users", schema=schema)
    table.rows = (
        Row((1, "Alice", 30)),
        Row((2, "Bob", 25)),
        Row((3, "Charlie", 35)),
    )

    projected_table = table.project(["id", "name"])
    assert projected_table.name == "users"
    assert len(projected_table.columns) == 2
    assert projected_table.columns[0].name == "id"
    assert projected_table.columns[1].name == "name"
    assert len(projected_table.rows) == 3
    assert projected_table.rows[0].row == (1, "Alice")
    assert projected_table.rows[1].row == (2, "Bob")
    assert projected_table.rows[2].row == (3, "Charlie")


def test_table_filtering():
    schema = Scehma(
        columns=[
            Column(name="id", col_type="INT"),
            Column(name="name", col_type="STR"),
            Column(name="age", col_type="INT"),
        ]
    )
    table = Table(name="users", schema=schema)
    table.rows = (
        Row((1, "Alice", 30)),
        Row((2, "Bob", 25)),
        Row((3, "Charlie", 35)),
    )

    condition = Condition(
        left=Column(name="age", col_type="INT"),
        operation=">",
        right=Literal(name="age_literal", value=30),
    )

    filtered_table = table.filter([condition])
    assert filtered_table.name == "users"
    assert len(filtered_table.columns) == 3
    assert len(filtered_table.rows) == 1
    assert filtered_table.rows[0].row == (3, "Charlie", 35)


def test_table_add_and_delete_row():
    schema = Scehma(
        columns=[
            Column(name="id", col_type="INT"),
            Column(name="name", col_type="STR"),
        ]
    )
    table = Table(name="users", schema=schema)

    row1 = Row((1, "Alice"))
    row2 = Row((2, "Bob"))

    table.add_row(row1)
    table.add_row(row2)

    assert len(table.rows) == 2
    assert table.rows[0].row == (1, "Alice")
    assert table.rows[1].row == (2, "Bob")

    table.delete_row_by_index(0)

    assert len(table.rows) == 1
    assert table.rows[0].row == (2, "Bob")


def test_table_count_rows():
    schema = Scehma(
        columns=[
            Column(name="id", col_type="INT"),
            Column(name="name", col_type="STR"),
        ]
    )
    table = Table(name="users", schema=schema)
    table.rows = (
        Row((1, "Alice")),
        Row((2, "Bob")),
        Row((3, "Charlie")),
    )

    assert table.count_rows() == 3
