from dataclasses import dataclass
from typing import Literal

# Abstract classes


class Expr:
    pass


class Query:
    pass


# Data classes


@dataclass
class TableRef:
    name: str
    alias: str | None


@dataclass
class Join:
    type: Literal["INNER", "LEFT", "RIGHT", "FULL"]
    table: TableRef
    on: Expr


@dataclass
class Lit(Expr):
    value: str | int | float | bool
    type: str


@dataclass
class Col(Expr):
    table: str | None  # alias or table name
    name: str


@dataclass
class BinaryExpr(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class LogicalExpr(Expr):
    left: Expr
    op: Literal["AND", "OR"]
    right: Expr


@dataclass
class UnaryExpr(Expr):
    op: str
    value: Expr


@dataclass
class SelectItem:
    value: Expr
    alias: str | None


@dataclass
class SelectQuery(Query):
    columns: list[SelectItem]
    table: TableRef
    joins: list[Join]
    where: Expr | None
