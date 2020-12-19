from enum import IntEnum
from collections import deque
from functools import reduce
import re
from typing import List


class TokenTypes(IntEnum):
    KEYWORD = 0
    SYMBOL = 1
    IDENTIFIER = 2
    INT_CONST = 3
    STRING_CONST = 4


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
    JACK_SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}
    JACK_KEYWORDS = {'CLASS', 'CONSTRUCTOR', 'FUNCTION', 'METHOD',
                     'FIELD', 'STATIC', 'VAR', 'INT', 'CHAR', 'BOOLEAN',
                     'VOID', 'TRUE', 'FALSE', 'NULL', 'THIS', 'LET', 'DO',
                     'IF', 'ELSE', 'WHILE', 'RETURN'}

    def __init__(self, jack_file_path: str):
        self.jack_file_tokens = self._load_file(jack_file_path)
        self._token_idx = 0
        self.current_token = None

    def has_more_tokens(self) -> bool:
        """
        Are there more tokens in the input?
        :return: bool.
        """
        return len(self.jack_file_tokens) > self._token_idx

    def advance(self) -> None:
        """
        Gets the next token from the input, and makes it the current token.
        This method should be called only if has_more_tokens is true
        Initially there is no current token.
        :return: None.
        """
        self.current_token = self.jack_file_tokens[self._token_idx]
        self._token_idx += 1

    def token_type(self) -> TokenTypes:
        """
        :return: The type of the current token, as a Enum.
        """
        if self.current_token.upper() in self.JACK_KEYWORDS:
            return TokenTypes.KEYWORD
        elif self.current_token in self.JACK_SYMBOLS:
            return TokenTypes.SYMBOL
        elif self.current_token.isdigit() and int(self.current_token) <= 32767:
            return TokenTypes.INT_CONST
        elif self.current_token.startswith('"') and self.current_token.endswith('"'):
            return TokenTypes.STRING_CONST
        else:
            return TokenTypes.IDENTIFIER

    def key_word(self) -> Keyword:
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

    def identifier(self) -> str:
        """
        This method should be called only if token_type is IDENTIFIER.
        :return: The identifier which is the current token
        """
        pass

    @staticmethod
    def _load_file(file_path: str) -> List[str]:
        """
        Prepares the data for the JackTokenizer, in an easier to work with format.
        Reads the file, removes all the comments, whitespaces.
        :param file_path: File path to work on.
        :return: A list with all the file components.
        """
        with open(file_path, 'r') as f:
            file_content = f.read()

        str_without_comments = re.sub('\/\*[\s\S]*?\*\/|([^\\:]|^)\/\/.*$', '', file_content, flags=re.MULTILINE)
        str_without_new_lines = str_without_comments.lstrip('\n').replace('\n', ' ')
        return JackTokenizer._split_keep_seperators(str_without_new_lines)

    @staticmethod
    def _split_keep_seperators(text: str) -> List[str]:
        all_matches = re.split('([{}\(\)\[\]\.,;\*&\|<>=~\+-\/ ])', text)
        return [curr_symbol for curr_symbol in all_matches if curr_symbol and curr_symbol != ' ']
