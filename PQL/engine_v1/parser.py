from PQL.engine_v1.models.lexer_models import Token
from PQL.engine_v1.models.parser_models import (
    ColumnExpr,
    Expr,
    Join,
    LiteralExpr,
    Query,
    SelectItem,
    SelectQuery,
    TableRef,
)


class Parser:
    tokens: list[Token]
    pos: int

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, expected_kind: str) -> Token:
        """
        Get and ensure next token is the expected kind, used for required clauses like FROM
        """
        token = self.current()
        if not token or token.kind != expected_kind:
            raise SyntaxError(f"Expected {expected_kind}, got {token}")
        self.pos += 1
        return token

    def match(self, expected_kind: str) -> Token | None:
        """
        Get next token if it matches expected kind, used for optional clauses like JOIN, WHERE
        """
        token = self.current()
        if not token or token.kind != expected_kind:
            return None
        self.pos += 1
        return token

    def parse(self) -> Query:
        current = self.current()

        if not current:
            raise ValueError("Query given is blank or invalid")

        kind = current.kind

        match kind:
            case "SELECT":
                return self.parse_select()

            case _:
                raise SyntaxError("Invalid query type")

    def parse_select(self) -> SelectQuery:
        self.eat("SELECT")
        columns = self.parse_select_columns()
        self.eat("FROM")
        from_table = self.parse_from_statement()

        joins: list[Join] = []  # future JOIN parsing
        where = None  # future WHERE parsing

        return SelectQuery(select=columns, from_=from_table, joins=joins, where=where)

    def parse_expression(self) -> Expr:
        tok = self.current()
        if not tok:
            raise SyntaxError("Unexpected end of input")
        elif tok.kind == "LPAREN":
            self.eat("LPAREN")
            expr = self.parse_expression()
            self.eat("RPAREN")
            return expr
        elif tok.kind == "IDENT":
            ident = self.eat("IDENT").value
            if self.match("DOT"):
                col = self.eat("IDENT").value
                return ColumnExpr(table=ident, name=col)  # type: ignore
            else:
                return ColumnExpr(table=None, name=ident)
        elif tok.kind in ("NUMBER", "STRING"):
            return LiteralExpr(value=self.eat(tok.kind).👌👌👌value)
        else:
            raise SyntaxError(f"Invalid expression: {tok}")

    # TODO Support Expressions like (SALARY + BONUS) * 0.77 AS NET_EARNINGS
    # Keeping simple as columns and literals for now
    def parse_select_columns(self) -> list[SelectItem]:
        items: list[SelectItem] = []

        while True:
            tok = self.current()
            if not tok:
                raise SyntaxError("Unexpected end of input")

            if tok.kind == "IDENT":
                ident = self.eat("IDENT").value

                if self.match("DOT"):
                    col = self.eat("IDENT").value
                    expr = ColumnExpr(table=ident, name=col)  # type: ignore
                else:
                    expr = ColumnExpr(table=None, name=ident)

            elif tok.kind in ("NUMBER", "STRING"):
                expr = LiteralExpr(value=self.eat(tok.kind).value)

            else:
                raise SyntaxError(f"Invalid select item: {tok}")

            alias = None
            if self.match("AS"):
                alias = self.eat("IDENT").value

            items.append(SelectItem(expr, alias))

            if not self.match("COMMA"):
                break

        return items

    def parse_from_statement(self) -> TableRef:
        current = self.eat("IDENT")
        alias = None

        if self.match("AS"):
            if alias_token := self.match("IDENT"):
                alias = alias_token.value
            else:
                raise SyntaxError("Invalid from alias")

        return TableRef(name=current.value, alias=alias)
