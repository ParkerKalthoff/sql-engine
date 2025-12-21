class Token:
    def __init__(self, kind: str, value: str) -> None:
        self.kind = kind
        self.value = value

    def __str__(self):
        return f"Token({self.kind}, {self.value})"

    def __eq__(self, other):  # type: ignore
        if not isinstance(other, Token):
            return False
        return self.kind == other.kind and self.value == other.value

    kind: str
    value: str
