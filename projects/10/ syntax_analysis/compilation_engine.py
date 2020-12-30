from jack_tokenizer import *
from xml.etree.ElementTree import TreeBuilder
from functools import singledispatchmethod


class CompilationEngine(TreeBuilder):
    """Generates the compiler's output"""
    CLASS_VAR_DEC_TOKENS = ["static", "field"]
    SUBROUTINE_TOKENS = ["function", "method", "constructor"]
    VARIABLE_TYPES = ['int', 'char', 'boolean']
    STATEMENT_TOKENS = ['do', 'let', 'while', 'return', 'if']

    def __init__(self, jack_tokenizer: JackTokenizer, output_path: str):
        super().__init__()
        self.output_path = open(output_path, 'w')
        self.tokenizer = jack_tokenizer
        self.tokenizer.advance()
        self.compile_class()

    def compile_class(self) -> None:
        """
        Compiles a complete class
        :return: None
        """
        self.start('class')
        self._consume('class')
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
        self.end('class')

    def compile_class_var_dec(self) -> None:
        """
        Compiles static variable declaration, or a field declaration
        :return: None.
        """
        self.start('classVarDec')
        self._consume(self.CLASS_VAR_DEC_TOKENS)
        self._consume(self.VARIABLE_TYPES)
        self._consume(TokenTypes.IDENTIFIER)

        while self._get_current_token() != ';':
            self._consume(',')
            self._consume(TokenTypes.IDENTIFIER)

        self._consume(';')
        self.end('classVarDec')

    def compile_subroutine_dec(self) -> None:
        """
        Compiles a complete method, function or constructor.
        :return: None
        """
        self.start('subroutineDec')
        self._consume(self.SUBROUTINE_TOKENS)
        self._consume(self.VARIABLE_TYPES.append('void'))  # ['int', 'char', 'boolean', 'void']
        self._consume(TokenTypes.IDENTIFIER)
        self._consume('(')
        self.compile_parameter_list()
        self._consume(')')
        self.compile_subroutine_body()
        self.end('subroutineDec')

    def compile_parameter_list(self) -> None:
        """
        Compiles a (possibly empty) parameter list. Doesn't handle the enclosing "()".
        :return:
        """
        self.start('parameterList')
        if self._get_current_token() != ')':
            self._consume(self.VARIABLE_TYPES)
            self._consume(TokenTypes.IDENTIFIER)
            while self._get_current_token() != ')':
                self._consume(',')
                self._consume(self.VARIABLE_TYPES)
                self._consume(TokenTypes.IDENTIFIER)

        self.end('parameterList')

    def compile_subroutine_body(self) -> None:
        """
        Compiles a subroutine's body.
        :return: None
        """
        self.start('subroutineBody')
        self._consume('{')
        while self._get_current_token() == 'var':
            self.compile_var_dec()
        while self._get_current_token() != '}':
            self.compile_statements()

        self._consume('}')
        self.end('subroutineBody')

    def compile_var_dec(self) -> None:
        """
        Compiles a var declaration.
        :return: None.
        """
        self.start('varDec')
        self._consume('var')
        self._consume(self.VARIABLE_TYPES)
        self._consume(TokenTypes.IDENTIFIER)
        while self._get_current_token() != ';':
            self._consume(',')
            self._consume(TokenTypes.IDENTIFIER)

        self._consume(';')
        self.end('varDec')

    def compile_statements(self) -> None:
        """
        Compiles a sequence of statements. Doesn't handle the enclosing "{}".
        :return: None.
        """
        self.start('statements')

        while self._get_current_token() != '}':
            if self._get_current_token() == 'let':
                self.compile_let()
            elif self._get_current_token() == 'if':
                self.compile_if()
            elif self._get_current_token() == 'while':
                self.compile_while()
            elif self._get_current_token() == 'do':
                self.compile_do()
            elif self._get_current_token() == 'return':
                self.compile_return()
            else:
                raise CompilationEngineError(f"{self._get_current_token()} is an expected token at this point")

        self.end('statements')

    def compile_do(self) -> None:
        """
        Compiles a do statement.
        :return: None.
        """
        self.start('doStatement')
        self._consume('do')
        # TODO: Should compile subroutine_call here...
        self.end('doStatement')

    def compile_let(self) -> None:
        """
        Compiles a let statement.
        :return: None.
        """
        self.start('letStatement')
        self._consume('let')
        self._consume(TokenTypes.IDENTIFIER)
        if self._get_current_token() == '[':
            self._consume('[')
            self.compile_expression()
            self._consume(']')

        self._consume('=')
        self.compile_expression()
        self._consume(';')
        self.end('letStatement')

    def compile_while(self) -> None:
        """
        Compiles a while statement.
        :return: None.
        """
        self.start('whileStatement')
        self._consume('while')
        self._consume('(')
        self.compile_expression()
        self._consume(')')

        self._consume('{')
        self.compile_statements()
        self._consume('}')
        self.end('whileStatement')

    def compile_return(self) -> None:
        """
        Compiles a return statement.
        :return: None.
        """
        self.start('returnStatement')
        self._consume('return')
        if self._get_current_token() != ';':
            self.compile_expression()
        self._consume(';')
        self.end('returnStatement')

    def compile_if(self) -> None:
        """
        Compiles an if statement, possibly with a trailing else clause.
        :return: None.
        """
        self.start('ifStatement')
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

        self.start('ifStatement')

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
            self._write_current_terminal_token()
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
