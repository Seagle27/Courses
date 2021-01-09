from functools import singledispatchmethod

from jack_tokenizer import *
from vm_writer import VMWriter
from symbol_table import *


class CompilationEngine:
    """Generates the compiler's output"""
    CLASS_VAR_DEC_TOKENS = ["static", "field"]
    SUBROUTINE_TOKENS = ["function", "method", "constructor"]
    VARIABLE_TYPES = ['int', 'char', 'boolean']
    STATEMENT_TOKENS = ['do', 'let', 'while', 'return', 'if']
    OP = ['+', '-', '*', '/', '&', '|', '<', '>', '=']

    def __init__(self, jack_tokenizer: JackTokenizer, output_path: str):
        super().__init__()
        self.tokenizer = jack_tokenizer
        self.writer = VMWriter(output_path)
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
        self.class_name = ''
        self.compile_class()

    def compile_class(self) -> None:
        """
        Compiles a complete class
        :return: None
        """
        self._consume('class')
        if self.tokenizer.token_type() != TokenTypes.IDENTIFIER:
            raise CompilationEngineError(f"{self._get_current_token()} is an invalid token at this point. Expected a "
                                         f"class name.")

        self.class_name = self._get_current_token()
        self._consume(TokenTypes.IDENTIFIER)
        self._consume('{')

        while self._get_current_token() != '}':
            if self._get_current_token() in CompilationEngine.CLASS_VAR_DEC_TOKENS:
                self.compile_class_var_dec()
            elif self._get_current_token() in CompilationEngine.SUBROUTINE_TOKENS:
                self.compile_subroutine_dec()
            else:
                raise CompilationEngineError(f"{self._get_current_token()} is an expected token at this point")

        self._consume('}')

    def compile_class_var_dec(self) -> None:
        """
        Compiles static variable declaration, or a field declaration
        :return: None.
        """
        self._consume(self.CLASS_VAR_DEC_TOKENS)
        self._consume_type()

        self._consume(TokenTypes.IDENTIFIER)

        while self._get_current_token() != ';':
            self._consume(',')
            self._consume(TokenTypes.IDENTIFIER)

        self._consume(';')

    def compile_subroutine_dec(self) -> None:
        """
        Compiles a complete method, function or constructor.
        :return: None
        """
        self._consume(self.SUBROUTINE_TOKENS)
        try:
            self._consume_type()
        except CompilationEngineError:
            self._consume('void')
        self._consume(TokenTypes.IDENTIFIER)
        self._consume('(')
        self.compile_parameter_list()
        self._consume(')')
        self.compile_subroutine_body()

    def compile_parameter_list(self) -> None:
        """
        Compiles a (possibly empty) parameter list. Doesn't handle the enclosing "()".
        :return:
        """
        if self._get_current_token() != ')':
            self._consume_type()

            self._consume(TokenTypes.IDENTIFIER)
            while self._get_current_token() != ')':
                self._consume(',')
                self._consume_type()

                self._consume(TokenTypes.IDENTIFIER)

    def compile_subroutine_body(self) -> None:
        """
        Compiles a subroutine's body.
        :return: None
        """
        self._consume('{')
        while self._get_current_token() == 'var':
            self.compile_var_dec()
        while self._get_current_token() != '}':
            self.compile_statements()

        self._consume('}')

    def compile_var_dec(self) -> None:
        """
        Compiles a var declaration.
        :return: None.
        """
        self._consume('var')
        self._consume_type()
        self._consume(TokenTypes.IDENTIFIER)
        while self._get_current_token() != ';':
            self._consume(',')
            self._consume(TokenTypes.IDENTIFIER)

        self._consume(';')

    def compile_statements(self) -> None:
        """
        Compiles a sequence of statements. Doesn't handle the enclosing "{}".
        :return: None.
        """
        while self._get_current_token() != '}':
            if self._get_current_token() in self.STATEMENT_TOKENS:
                getattr(self, 'compile_' + self._get_current_token())()
            else:
                raise CompilationEngineError(f"{self._get_current_token()} is an expected token at this point")

    def compile_do(self) -> None:
        """
        Compiles a do statement.
        :return: None.
        """
        self._consume('do')
        self.compile_subroutine_call()
        self._consume(';')

    def compile_let(self) -> None:
        """
        Compiles a let statement.
        :return: None.
        """
        self._consume('let')
        self._consume(TokenTypes.IDENTIFIER)
        if self._get_current_token() == '[':
            self._consume('[')
            self.compile_expression()
            self._consume(']')

        self._consume('=')
        self.compile_expression()
        self._consume(';')

    def compile_while(self) -> None:
        """
        Compiles a while statement.
        :return: None.
        """
        self._consume('while')
        self._consume('(')
        self.compile_expression()
        self._consume(')')

        self._consume('{')
        self.compile_statements()
        self._consume('}')

    def compile_return(self) -> None:
        """
        Compiles a return statement.
        :return: None.
        """
        self._consume('return')
        if self._get_current_token() != ';':
            self.compile_expression()
        self._consume(';')

    def compile_if(self) -> None:
        """
        Compiles an if statement, possibly with a trailing else clause.
        :return: None.
        """
        self._consume('if')
        self._consume('(')
        self.compile_expression()
        self._consume(')')

        self._consume('{')
        self.compile_statements()
        self._consume('}')

        if self._get_current_token() == 'else':
            self._consume('else')
            self._consume('{')
            self.compile_statements()
            self._consume('}')

    def compile_expression(self) -> None:
        """
        Compiles an expression.
        :return: None
        """
        self.compile_term()
        while self._get_current_token() in self.OP:
            self._consume(self.OP)
            self.compile_term()

    def compile_term(self) -> None:
        """
        Compiles a term. If the current token is an identifier, the routine must distinguish between a variable,
        an array entry, or a subroutine call.
        :return: None.
        """
        token_type = self.tokenizer.token_type()
        if token_type == TokenTypes.IDENTIFIER:
            curr_token = self._get_current_token()
            self.tokenizer.advance()
            if self._get_current_token() in ('(', '.'):
                self.compile_subroutine_call(curr_token)
            else:
                if self._get_current_token() == '[':
                    self._consume('[')
                    self.compile_expression()
                    self._consume(']')
        elif token_type in [token_type.INT_CONST, token_type.KEYWORD]:
            self._consume(token_type)
        elif token_type == token_type.STRING_CONST:
            const_str = ''
            first = True
            while const_str.count('"') < 2:
                if first:
                    const_str += self._get_current_token()
                    first = False
                else:
                    const_str += ' ' + self._get_current_token()
                if self.tokenizer.has_more_tokens():
                    self.tokenizer.advance()

        else:
            if self._get_current_token() == '(':
                self._consume('(')
                self.compile_expression()
                self._consume(')')
            else:
                self._consume(['-', '~'])  # unaryOp term
                self.compile_term()

    def compile_subroutine_call(self, subroutine_name=None) -> None:
        if not subroutine_name:
            self._consume(TokenTypes.IDENTIFIER)

        if self._get_current_token() == '.':
            self._consume('.')
            self._consume(TokenTypes.IDENTIFIER)

        self._consume('(')
        self.compile_expression_list()
        self._consume(')')

    def compile_expression_list(self) -> None:
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        :return: None.
        """
        if self._get_current_token() != ')':
            self.compile_expression()
            while self._get_current_token() == ',':
                self._consume(',')
                self.compile_expression()

    @singledispatchmethod
    def _consume(self, expected) -> None:
        """
        Check if the current token matches what it's expected to be. Either by value or by type.
        In case of a match, the function will advance to the next token.
        Otherwise the function will raise CompilationEngineError.
        :return: None
        """
        raise TypeError("Unsupported type: ", type(expected))

    @_consume.register(str)
    @_consume.register(list)
    def _(self, expected_tokens) -> None:
        """Consume by value"""
        if not isinstance(expected_tokens, list):
            expected_tokens = [expected_tokens]

        curr_token = self._get_current_token()
        if curr_token not in expected_tokens:
            raise CompilationEngineError(f"Expected {expected_tokens} but current token is {curr_token}. "
                                         f"Compilation failed.")
        else:
            if self.tokenizer.has_more_tokens():
                self.tokenizer.advance()

    @_consume.register
    def _(self, expected_types: TokenTypes):
        """Consume by type"""
        if not isinstance(expected_types, list):
            expected_types = [expected_types]
        curr_type = self.tokenizer.token_type()
        if curr_type not in expected_types:
            raise CompilationEngineError(f"Expected {expected_types} but current token type is {curr_type}. "
                                         f"Compilation failed.")
        else:
            if self.tokenizer.has_more_tokens():
                self.tokenizer.advance()

    def _consume_type(self):
        """
        Int / char / boolean / class name
        :return: None.
        """
        try:
            self._consume(self.VARIABLE_TYPES)
        except CompilationEngineError:
            self._consume(TokenTypes.IDENTIFIER)  # Class name

    def _get_current_token(self) -> str:
        token_type = self.tokenizer.token_type()
        if token_type is TokenTypes.INT_CONST:
            curr_token = str(self.tokenizer.int_val())
        elif token_type is TokenTypes.KEYWORD:
            curr_token = self.tokenizer.key_word()
        else:
            curr_token = self.tokenizer.current_token

        return curr_token


class CompilationEngineError(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        if self.message:
            return self.message
        else:
            return "Unexpected token. Compilation failed"
