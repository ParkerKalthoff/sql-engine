from PQL.engine_v1.models.lexer_models import Token
from PQL.engine_v1.models.parser_models import Col, Query, SelectItem, SelectQuery


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
        self.eat("FROM")
        self.match("WHERE")
        raise SyntaxError()

    # TODO Support Expressions like (SALARY + BONUS) - TAXES AS NET_EARNINGS
    # Keeping simple as columns for now
    def parse_select_columns(self) -> None:
        """
        Parses tokens to construct Column or Literal objects
        """
        current = self.current()
        if not current:
            raise SyntaxError()
        columns: list[SelectItem] = []

        kind = current.kind
        value = current.value

        while True:
            match kind:
                case "IDENT":
                    if self.match("DOT"):
                        if epr_val := self.match("IDENT"):
                            expression = Col(table=value, value=epr_val)

                        else:
                            raise SyntaxError(
                                "Missing Identifier after table qualifier"
                            )

                case "NUMBER":
                    expression_value = ""
                case "STRING":
                    expression_value = ""
                case _:
                    raise SyntaxError(f"Attempted to parse {kind} as select column")
