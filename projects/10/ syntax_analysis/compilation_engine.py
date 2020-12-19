
class CompilationEngine:
    """Generates the compiler's output"""

    def __init__(self, jack_filename: str, output_path: str):
        pass

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
