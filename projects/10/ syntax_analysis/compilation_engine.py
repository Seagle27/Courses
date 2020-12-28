from jack_tokenizer import *
from xml.etree.ElementTree import TreeBuilder


class CompilationEngine(TreeBuilder):
    """Generates the compiler's output"""
    CLASS_VAR_DEC_TOKENS = ["static", "field"]
    SUBROUTINE_TOKENS = ["function", "method", "constructor"]
    VARIABLE_TYPES = ['int', 'char', 'boolean']
    STATEMENT_TOKENS = ['do', 'let', 'while', 'return', 'if']

    def __init__(self, jack_tokenizer: JackTokenizer, output_path: str):
        super().__init__()
        self.output_path = output_path
        self.tokenizer = jack_tokenizer
        self.compile_class()

    def compile_class(self) -> None:
        """
        Compiles a complete class
        :return: None
        """
        self.start('class')
        self._consume_by_token('class')
        self._consume_by_type(TokenTypes.IDENTIFIER)
        self._consume_by_token('{')

        while self._get_current_token() != '}':
            if self._get_current_token() in CompilationEngine.CLASS_VAR_DEC_TOKENS:
                self.compile_class_var_dec()
            elif self._get_current_token() in CompilationEngine.SUBROUTINE_TOKENS:
                self.compile_subroutine_dec()
            else:
                raise CompilationEngineError(f"{self._get_current_token()} is an expected token at this point")

        self._consume_by_token('}')
        self.end('class')

    def compile_class_var_dec(self) -> None:
        """
        Compiles static variable declaration, or a field declaration
        :return: None.
        """
        self.start('classVarDec')
        self._consume_by_token(self.CLASS_VAR_DEC_TOKENS)
        self._consume_by_token(self.VARIABLE_TYPES)
        self._consume_by_type(TokenTypes.IDENTIFIER)

        while self._get_current_token() != ';':
            self._consume_by_token(',')
            self._consume_by_type(TokenTypes.IDENTIFIER)

        self._consume_by_token(';')
        self.end('classVarDec')

    def compile_subroutine_dec(self) -> None:
        """
        Compiles a complete method, function or constructor.
        :return: None
        """
        self.start('subroutineDec')
        self._consume_by_token(self.SUBROUTINE_TOKENS)
        self._consume_by_token(self.VARIABLE_TYPES.append('void'))  # ['int', 'char', 'boolean', 'void']
        self._consume_by_type(TokenTypes.IDENTIFIER)
        self._consume_by_token('(')
        self.compile_parameter_list()
        self._consume_by_token(')')
        self.compile_subroutine_body()
        self.end('subroutineDec')

    def compile_parameter_list(self) -> None:
        """
        Compiles a (possibly empty) parameter list. Doesn't handle the enclosing "()".
        :return:
        """
        self.start('parameterList')
        if self._get_current_token() != ')':
            self._consume_by_token(self.VARIABLE_TYPES)
            self._consume_by_type(TokenTypes.IDENTIFIER)
            while self._get_current_token() != ')':
                self._consume_by_token(',')
                self._consume_by_token(self.VARIABLE_TYPES)
                self._consume_by_type(TokenTypes.IDENTIFIER)

        self.end('parameterList')

    def compile_subroutine_body(self) -> None:
        """
        Compiles a subroutine's body.
        :return: None
        """
        pass

    def compile_var_dec(self) -> None:
        """
        Compiles a var declaration.
        :return: None.
        """
        pass

    def compile_statements(self) -> None:
        """
        Compiles a sequence of statements. Doesn't handle the enclosing "{}".
        :return: None.
        """
        pass

    def compile_do(self) -> None:
        """
        Compiles a do statement.
        :return: None.
        """
        pass

    def compile_let(self) -> None:
        """
        Compiles a let statement.
        :return: None.
        """
        pass

    def compile_while(self) -> None:
        """
        Compiles a while statement.
        :return: None.
        """
        pass

    def compile_return(self) -> None:
        """
        Compiles a return statement.
        :return: None.
        """
        pass

    def compile_if(self) -> None:
        """
        Compiles an if statement, possibly with a trailing else clause.
        :return: None.
        """
        pass

    def compile_expression(self) -> None:
        """
        Compiles an expression.
        :return: None
        """
        pass

    def compile_term(self) -> None:
        """
        Compiles a term. If the current token is an identifier, the routine must distinguish between a variable,
        an array entry, or a subroutine call.
        :return: None.
        """
        pass

    def compile_expression_list(self) -> None:
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        :return: None.
        """
        pass

    def _consume_by_token(self, expected_tokens: str or List[str]):
        if not isinstance(expected_tokens, list):
            expected_token = [expected_tokens]

        curr_token = self._get_current_token()
        if curr_token not in expected_tokens:
            raise CompilationEngineError(f"Expected {expected_tokens} but current token is {curr_token}. "
                                         f"Compilation failed.")
        else:
            self._write_current_terminal_token()
            self.tokenizer.advance()

    def _consume_by_type(self, expected_types: TokenTypes or List[TokenTypes]):
        if not isinstance(expected_types, list):
            expected_types = [expected_types]
        curr_type = self._get_current_token()
        if curr_type not in expected_types:
            raise CompilationEngineError(f"Expected {expected_types} but current token type is {curr_type}. "
                                         f"Compilation failed.")
        else:
            self._write_current_terminal_token()
            self.tokenizer.advance()

    def start(self, tag, **kwargs):
        super().start(tag, {})

    def _write_current_terminal_token(self) -> None:
        token_type = self.tokenizer.token_type()
        if token_type is TokenTypes.INT_CONST:
            tag = "integerConstant"
        elif token_type is TokenTypes.STRING_CONST:
            tag = "StringConstant"
        else:
            tag = self.tokenizer.token_type().name.lower()

        self.start(tag)
        self.data(self._get_current_token())
        self.end(tag)

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
