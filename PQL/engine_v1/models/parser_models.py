from dataclasses import dataclass
from typing import Literal


class Expr:
    pass


@dataclass
class Lit(Expr):
    value: str | int | float | bool
    type: str


@dataclass
class Col(Expr):
    table: str | None
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


class Query:
    pass


@dataclass
class SelectQuery(Query):
    columns: list[SelectItem]
    table: str
    where: Expr | None
