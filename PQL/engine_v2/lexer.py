import re
from dataclasses import dataclass


@dataclass
class Token:
    kind: str
    value: str

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Token):
            return False
        return (self.kind == value.kind) and (self.value == value.value)

    def __repr__(self) -> str:
        return f"TOKEN({self.kind}, {self.value})"


TOKEN_SPEC = [
    ("SELECT", r"SELECT\b"),
    ("INSERT", r"INSERT\b"),
    ("UPDATE", r"UPDATE\b"),
    ("DELETE", r"DELETE\b"),
    ("FROM", r"FROM\b"),
    ("JOIN", r"JOIN\b"),
    ("ON", r"ON\b"),
    ("WHERE", r"WHERE\b"),
    ("GROUP", r"GROUP\b"),
    ("BY", r"BY\b"),
    ("HAVING", r"HAVING\b"),
    ("ORDER", r"ORDER\b"),
    ("LIMIT", r"LIMIT\b"),
    ("AS", r"AS\b"),
    ("COMMA", r","),
    ("STAR", r"\*"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("DOT", r"\."),
    ("BOOLEAN", r"TRUE|FALSE"),
    ("OP", r"<>|<=|>=|!=|=|<|>"),
    # Used to catch illegal identifiers before processing to simplify logic
    ("INVALID_NUMBER", r"\d+[a-zA-Z_]+"),
    ("NUMBER", r"\d+(\.\d+)?"),
    ("STRING", r"'[^']*'"),
    ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("WS", r"\s+"),
]

MASTER_RE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC),
    re.IGNORECASE,
)


class Lexer:
    """
    Class for transforming input string into tokens for parser to consume
    """

    def tokenize(self, text: str) -> list[Token]:
        """

        Method for transforming an input string to tokens to be consumed in a parser

        "SELECT AGE, SALARY, NAME FROM ACCOUNTS" ->

            [
                TOKEN(SELECT, SELECT),
                TOKEN(IDENT, AGE),
                TOKEN(COMMA, ,),
                TOKEN(IDENT, SALARY),
                TOKEN(COMMA, ,),
                TOKEN(IDENT, NAME),
                TOKEN(FROM, FROM),
                TOKEN(IDENT, ACCOUNTS)
            ]
        """

        text = text.upper()
        tokens: list[Token] = []
        pos = 0
        length = len(text)

        while pos < length:
            match = MASTER_RE.match(text, pos)
            if not match:
                raise SyntaxError(
                    f"Invalid token at position {pos}: {text[pos : pos + 10]!r}"
                )

            kind = match.lastgroup
            value = match.group()

            if not kind:
                raise SyntaxError("Unkown argument")

            if kind == "INVALID_NUMBER":
                raise SyntaxError("Numbers + Letters string detected")

            if kind != "WS":
                tokens.append(Token(kind, value))

            pos = match.end()

        return tokens
