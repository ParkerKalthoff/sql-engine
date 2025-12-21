from PQL.engine_v1.lexer import tokenize
from PQL.engine_v1.models.lexer_models import Token

"""
Test cases to ensure tokenizer extracts tokens from strings properly
"""


def test_invalid_tokens():
    test_cases: list[str] = ["123ABC"]

    for test_case in test_cases:
        try:
            tokenize(test_case)
            assert False
        except SyntaxError:
            pass


def test_valid_query_tokenization():
    test_cases: list[tuple[str, list[Token]]] = [
        (
            "SELECT * FROM ACCOUNT",
            [
                Token("SELECT", "SELECT"),
                Token("STAR", "*"),
                Token("FROM", "FROM"),
                Token("IDENT", "ACCOUNT"),
            ],
        ),
        (
            "SELECT NAME, ID FROM ACCOUNT WHERE 1.0 = 1",
            [
                Token("SELECT", "SELECT"),
                Token("IDENT", "NAME"),
                Token("COMMA", ","),
                Token("IDENT", "ID"),
                Token("FROM", "FROM"),
                Token("IDENT", "ACCOUNT"),
                Token("WHERE", "WHERE"),
                Token("NUMBER", "1.0"),
                Token("OP", "="),
                Token("NUMBER", "1"),
            ],
        ),
        (
            "SELECT NAME AS ACCOUNT_NAME, ID FROM ACCOUNT JOIN PURCHASES ON PURCHASES.ACCOUNT_ID = ACCOUNT.ID",
            [
                Token("SELECT", "SELECT"),
                Token("IDENT", "NAME"),
                Token("AS", "AS"),
                Token("IDENT", "ACCOUNT_NAME"),
                Token("COMMA", ","),
                Token("IDENT", "ID"),
                Token("FROM", "FROM"),
                Token("IDENT", "ACCOUNT"),
                Token("JOIN", "JOIN"),
                Token("IDENT", "PURCHASES"),
                Token("ON", "ON"),
                Token("IDENT", "PURCHASES"),
                Token("DOT", "."),
                Token("IDENT", "ACCOUNT_ID"),
                Token("OP", "="),
                Token("IDENT", "ACCOUNT"),
                Token("DOT", "."),
                Token("IDENT", "ID"),
            ],
        ),
    ]

    for test_case in test_cases:
        query = test_case[0]
        expected_result_tokens = test_case[1]

        result_tokens = tokenize(query)

        assert len(result_tokens) == len(expected_result_tokens)

        for result_token, expected_result_token in zip(
            result_tokens, expected_result_tokens
        ):
            assert result_token == expected_result_token
