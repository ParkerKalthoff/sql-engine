from PQL.engine_v1.models.lexer_models import Token
from PQL.engine_v1.parser import Parser
from PQL.engine_v1.models.parser_models import (
    ColumnExpr,
    LiteralExpr,
    SelectItem,
    SelectQuery,
    TableRef,
)


def t(kind: str, value: str) -> Token:
    """Shorthand for creating tokens"""
    return Token(kind, value)


def test_simple_select_single_column():
    tokens = [
        t("SELECT", "SELECT"),
        t("IDENT", "name"),
        t("FROM", "FROM"),
        t("IDENT", "users"),
    ]

    parser = Parser(tokens)
    query = parser.parse()

    assert isinstance(query, SelectQuery)
    assert query.from_ == TableRef(name="users", alias=None)
    assert len(query.select) == 1

    col = query.select[0]
    assert isinstance(col, SelectItem)
    assert isinstance(col.expr, ColumnExpr)
    assert col.expr.name == "name"
    assert col.expr.table is None
    assert col.alias is None


def test_select_multiple_columns():
    tokens = [
        t("SELECT", "SELECT"),
        t("IDENT", "id"),
        t("COMMA", ","),
        t("IDENT", "email"),
        t("FROM", "FROM"),
        t("IDENT", "users"),
    ]

    query: SelectQuery = Parser(tokens).parse()  # type: ignore

    assert len(query.select) == 2
    assert query.select[0].expr.name == "id"  # type: ignore
    assert query.select[1].expr.name == "email"  # type: ignore


def test_select_qualified_column():
    tokens = [
        t("SELECT", "SELECT"),
        t("IDENT", "users"),
        t("DOT", "."),
        t("IDENT", "id"),
        t("FROM", "FROM"),
        t("IDENT", "users"),
    ]

    query: SelectQuery = Parser(tokens).parse()  # type: ignore

    col = query.select[0].expr
    assert isinstance(col, ColumnExpr)
    assert col.table == "users"
    assert col.name == "id"


def test_select_literal_number():
    tokens = [
        t("SELECT", "SELECT"),
        t("NUMBER", "42"),
        t("FROM", "FROM"),
        t("IDENT", "dual"),
    ]

    query: SelectQuery = Parser(tokens).parse()  # type: ignore

    lit = query.select[0].expr
    assert isinstance(lit, LiteralExpr)
    assert lit.value == "42"


def test_select_column_alias():
    tokens = [
        t("SELECT", "SELECT"),
        t("IDENT", "name"),
        t("AS", "AS"),
        t("IDENT", "username"),
        t("FROM", "FROM"),
        t("IDENT", "users"),
    ]

    query: SelectQuery = Parser(tokens).parse()  # type: ignore

    item = query.select[0]
    assert item.alias == "username"  # type: ignore


def test_from_table_alias():
    tokens = [
        t("SELECT", "SELECT"),
        t("IDENT", "id"),
        t("FROM", "FROM"),
        t("IDENT", "users"),
        t("AS", "AS"),
        t("IDENT", "u"),
    ]

    query: SelectQuery = Parser(tokens).parse()  # type: ignore

    assert query.from_ == TableRef(name="users", alias="u")  # type: ignore


def test_invalid_missing_from():
    tokens = [
        t("SELECT", "SELECT"),
        t("IDENT", "id"),
    ]

    parser = Parser(tokens)
    try:
        parser.parse()
        assert False
    except SyntaxError:
        pass


def test_invalid_select_item():
    tokens = [
        t("SELECT", "SELECT"),
        t("FROM", "FROM"),
        t("IDENT", "users"),
    ]

    parser = Parser(tokens)
    try:
        parser.parse()
        assert False
    except SyntaxError:
        pass
