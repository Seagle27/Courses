from jack_tokenizer import *
from xml.etree.ElementTree import TreeBuilder


class CompilationEngine(TreeBuilder):
    """Generates the compiler's output"""

    TERMINAL_TOKEN_TYPES = ["STRING_CONST", "INT_CONST", "IDENTIFIER", "SYMBOL"]
    TERMINAL_KEYWORDS = ["boolean", "class", "void", "int"]

    def __init__(self, jack_tokenizer: JackTokenizer, output_path: str):
        super().__init__()
        self.output_path = output_path
        self.tokenizer = jack_tokenizer
        self.start('tokens')
        self.compile_class()
        self.end('tokens')

    def compile_class(self) -> None:
        """
        Compiles a complete class
        :return: None
        """
        pass

    def compile_class_var_dec(self) -> None:
        """
        Compiles static variable declaration, or a field declaration
        :return: None.
        """
        pass

    def compile_subroutine_dec(self) -> None:
        """
        Compiles a complete method, function or constructor.
        :return: None
        """
        pass

    def compile_parameter_list(self) -> None:
        """
        Compiles a (possibly empty) parameter list. Doesn't handle the enclosing "()".
        :return:
        """
        pass

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

    def _consume_token(self, expected_token: str):
        curr_token = self._get_current_token()
        if expected_token != curr_token:
            raise CompilationEngineError(f"Expected {expected_token} but current token is {curr_token}. "
                                         f"Compilation failed.")
        else:
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
            curr_token = self.tokenizer.int_val()
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
