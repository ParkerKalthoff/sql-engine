from dataclasses import dataclass
from typing import Literal, Optional, List, Union


# =========================
# Base AST node classes
# =========================


class Node:
    """Base class for all AST nodes."""

    pass


class Expr(Node):
    """Base class for all expressions."""

    pass


class Query(Node):
    """Base class for all queries."""

    pass


class FromItem(Node):
    """Base class for items that can appear in FROM or JOIN clauses."""

    alias: Optional[str] = None


@dataclass
class BinaryExpr(Expr):
    left: Expr
    op: Literal["+", "-", "*", "/", "=", "!=", "<", "<=", ">", ">=", "AND", "OR"]
    right: Expr


@dataclass
class UnaryExpr(Expr):
    op: Literal["NOT", "-"]
    operand: Expr


@dataclass
class LiteralExpr(Expr):
    value: Union[str, int, float, bool]


@dataclass
class ColumnExpr(Expr):
    table: Optional[str]  # table name or alias
    name: str


@dataclass
class TableRef(FromItem):
    name: str
    alias: Optional[str] = None


@dataclass
class SubqueryRef(FromItem):
    query: Query
    alias: Optional[str] = None


@dataclass
class Join(Node):
    type: Literal["INNER", "LEFT", "RIGHT", "FULL"]
    right: FromItem
    condition: Expr


@dataclass
class SelectItem(Node):
    expr: Expr
    alias: Optional[str] = None


@dataclass
class OrderByItem(Node):
    expr: Expr
    direction: Literal["ASC", "DESC"] = "ASC"


@dataclass
class SelectQuery(Query):
    select: List[SelectItem]
    from_: FromItem

    joins: Optional[List[Join]] = None
    where: Optional[Expr] = None
    group_by: Optional[List[Expr]] = None
    having: Optional[Expr] = None
    order_by: Optional[List[OrderByItem]] = None
    limit: Optional[int] = None

    # Only used when this query is referenced as a subquery
    alias: Optional[str] = None
