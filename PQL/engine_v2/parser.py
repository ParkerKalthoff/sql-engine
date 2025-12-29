from dataclasses import dataclass
from typing import Any, Literal as Lit
from lexer import Token


class ASTNode:
    pass


class Value(ASTNode):
    """
    Anything that can appear in an expression position:
    - column refs
    - literals
    - expressions
    - subqueries
    """

    pass


class ASTQuery(Value):
    """
    Base class for queries.
    Queries are Values so they can appear as subqueries.
    """

    pass


@dataclass
class ColumnRef(Value):
    """
    AGE
    accounts.age
    accounts.age AS user_age
    """

    name: str
    table: str | None
    alias: str | None


@dataclass
class Literal(Value):
    """
    1, 'hello', true
    """

    value: Any
    alias: str | None


@dataclass
class Expression(Value):
    """
    (SALARY + BONUS) * 0.77 AS EXPECTED_NET
    """

    left: Value
    operator: str
    right: Value | None
    alias: str | None


@dataclass
class Subquery(Value):
    query: "SelectQuery"
    alias: str | None


@dataclass
class TableRef(ASTNode):
    name: str
    alias: str | None


@dataclass
class FromItem(ASTNode):
    """
    FROM table
    FROM (SELECT ...) AS t
    """

    source: TableRef | Subquery


@dataclass
class Join(ASTNode):
    type: Lit["LEFT", "RIGHT", "INNER", "FULL OUTER"]
    source: TableRef | Subquery
    on: Value
    """
    ON account.id = user.id
    """


@dataclass
class SelectQuery(ASTQuery):
    selectItems: list[Value]
    fromItem: FromItem
    whereItem: Value | None
    groupByItem: list[Value] | None
    havingItem: Value | None
    orderByItem: list[Value] | None


class Parser:
    """
    Class for generating an AST from tokens
    """

    counter: int
    """Position of where the next item is"""
    tokens: list[Token]
    current_token: Token

    def __init__(self, tokens: list[Token]) -> None:
        if not tokens:
            raise ValueError

        self.tokens = tokens
        self.counter = 0

    def eat(self, expectedKind: str) -> Token:
        """Pass in a required next token kind, ensures next token is of correct kind, and emits next token"""
        if self.tokens[self.counter].kind != expectedKind:
            raise SyntaxError
        self.current_token = self.tokens[self.counter]
        self.counter += 1
        return self.current_token

    def match(self, expectedKind: str) -> Token | None:
        """Pass in a required next token kind, ensures next token is of correct kind, and emits next to or returns None if not so"""
        if self.tokens[self.counter].kind != expectedKind:
            return None
        self.current_token = self.tokens[self.counter]
        self.counter += 1
        return self.current_token

    def parse(self) -> ASTQuery:
        if self.match("SELECT"):
            return self.parse_select()
        else:
            raise SyntaxError

    def parse_values(self) -> list[Value]:
        pass

    def parse_select(self) -> SelectQuery:
        # SELECT -> (LITERAL, EXPRESSION, COLUMN, SUBQUERY? (not doing for now)) -> FROM -> (TABLEREF, SUBQUERY) -> WHERE -> EXPRESSION

        # SELECT has already been matched
        selectItems = self.parse_values()
        self.eat("FROM")

        if self.match("LPAREN"):
            # Subquery
            self.eat("SELECT")
            subquery: Subquery = self.parse_select()

        selectAST = SelectQuery(selectItems=selectItems)
        return selectAST
