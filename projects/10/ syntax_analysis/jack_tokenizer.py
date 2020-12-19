from enum import IntEnum


class TokenTypes(IntEnum):
    KEYWORD_SYMBOL = 0
    IDENTIFIER = 1
    INT_CONST = 2
    STRING_CONST = 3


class Keyword(IntEnum):
    CLASS = 0
    CONSTRUCTOR = 1
    FUNCTION = 2
    METHOD = 3
    FIELD = 4
    STATIC = 5
    VAR = 6
    INT = 7
    CHAR = 8
    BOOLEAN = 9
    VOID = 10
    TRUE = 11
    FALSE = 12
    NULL = 13
    THIS = 14
    LET = 15
    DO = 16
    IF = 17
    ELSE = 18
    WHILE = 19
    RETURN = 20


class JackTokenizer:
    """
    Ignores all comments and white space in the input stream, and serializes it into jack-language tokens.
    """
    def __init__(self, jack_file_path: str):
        self.jack_file_stream = open(jack_file_path, 'r')

    def has_more_tokens(self) -> bool:
        """
        Are there more tokens in the input?
        :return: bool.
        """
        pass

    def advance(self) -> None:
        """
        Gets the next token from the input, and makes it the current token.
        This method should be called only if has_more_tokens is true
        Initially there is no current token.
        :return: None.
        """
        pass

    def token_type(self) -> TokenTypes:
        """
        :return: The type of the current token, as a Enum.
        """
        pass

    def keyword(self) -> Keyword:
        """
        This method should be called only if token_type is KEYWORD.
        :return: The Keyword which is the current token as a Enum.
        """
        pass

    def symbol(self) -> str:
        """
        This method should be called only if token_type is SYMBOL.
        :return: The character which is the current token
        """
        pass

    @staticmethod
    def _remove_whitespace_and_comments(line) -> str:
        return line.strip().split("//")[0].strip()
