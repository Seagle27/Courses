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
    OP = {'+': 'ADD', '-': 'SUB', '&': 'AND', '|': 'OR', '<': 'LT', '>': 'GT', '=': 'EQ', '*': 'Math.multiply',
          '/': 'Math.divide'}

    def __init__(self, jack_tokenizer: JackTokenizer, output_path: str):
        super().__init__()
        self.tokenizer = jack_tokenizer
        self.table = SymbolTable()
        self.writer = VMWriter(output_path)
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

        self.class_name = ''
        self.curr_func_name = ''
        self._if_count = 0
        self._while_count = 0

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
        kind = str_to_kind(self._get_current_token())
        self._consume(self.CLASS_VAR_DEC_TOKENS)
        var_type = self._get_current_token()
        self._consume_type()

        self.table.define(self._get_current_token(), var_type, kind)
        self._consume(TokenTypes.IDENTIFIER)

        while self._get_current_token() != ';':
            self._consume(',')
            self.table.define(self._get_current_token(), var_type, kind)
            self._consume(TokenTypes.IDENTIFIER)

        self._consume(';')

    def compile_subroutine_dec(self) -> None:
        """
        Compiles a complete method, function or constructor.
        :return: None
        """
        self.table.reset()
        subroutine_type = self._get_current_token()
        if subroutine_type == 'method':
            self.table.define('this', self.class_name, Kind.ARG)  # Put this as the first arg in case it's a
            # class method
        self._consume(self.SUBROUTINE_TOKENS)
        try:
            self._consume_type()
        except CompilationEngineError:
            self._consume('void')

        self.curr_func_name = f'{self.class_name}.{self._get_current_token()}'
        self._consume(TokenTypes.IDENTIFIER)
        self._consume('(')
        self.compile_parameter_list()
        self._consume(')')
        self.compile_subroutine_body(subroutine_type)

    def compile_parameter_list(self) -> None:
        """
        Compiles a (possibly empty) parameter list. Doesn't handle the enclosing "()".
        :return:
        """
        if self._get_current_token() != ')':
            var_type = self._get_current_token()
            self._consume_type()

            self.table.define(self._get_current_token(), var_type, Kind.ARG)
            self._consume(TokenTypes.IDENTIFIER)
            while self._get_current_token() != ')':
                self._consume(',')
                var_type = self._get_current_token()
                self._consume_type()

                self.table.define(self._get_current_token(), var_type, Kind.ARG)
                self._consume(TokenTypes.IDENTIFIER)

    def compile_subroutine_body(self, subroutine_type: str) -> None:
        """
        Compiles a subroutine's body.
        :return: None
        """
        self._consume('{')
        while self._get_current_token() == 'var':
            self.compile_var_dec()
        var_count = self.table.var_count(Kind.VAR)
        self.writer.write_function(self.curr_func_name, var_count)

        if subroutine_type == 'constructor':
            n_fields = self.table.var_count(Kind.FIELD)
            self.writer.write_push('CONST', n_fields)
            self.writer.write_call('Memory.alloc', 1)
            self.writer.write_pop('POINTER', 0)
        elif subroutine_type == 'method':
            self.writer.write_push('ARG', 0)
            self.writer.write_pop('POINTER', 0)

        while self._get_current_token() != '}':
            self.compile_statements()

        self._consume('}')

    def compile_var_dec(self) -> None:
        """
        Compiles a var declaration.
        :return: None.
        """
        self._consume('var')
        var_type = self._get_current_token()
        self._consume_type()
        self.table.define(self._get_current_token(), var_type, Kind.VAR)
        self._consume(TokenTypes.IDENTIFIER)

        while self._get_current_token() != ';':
            self._consume(',')
            self.table.define(self._get_current_token(), var_type, Kind.VAR)
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
        self.writer.write_pop('TEMP', 0)  # void method
        self._consume(';')

    def compile_let(self) -> None:
        """
        Compiles a let statement.
        :return: None.
        """
        self._consume('let')
        name = self._get_current_token()
        kind = convert_kind(self.table.kind_of(name))
        index = self.table.index_of(name)

        self._consume(TokenTypes.IDENTIFIER)
        if self._get_current_token() == '[':
            self._consume('[')
            self.compile_expression()
            self._consume(']')

            self.writer.write_push(kind, index)
            self.writer.write_arithmetic('ADD')
            self.writer.write_pop('TEMP', 0)

            self._consume('=')
            self.compile_expression()
            self.writer.write_push('TEMP', 0)
            self.writer.write_pop('POINTER', 1)
            self.writer.write_pop('THAT', 0)

        else:
            self._consume('=')
            self.compile_expression()
            self.writer.write_pop(kind, index)

        self._consume(';')

    def compile_while(self) -> None:
        """
        Compiles a while statement.
        :return: None.
        """
        self._consume('while')
        self._consume('(')

        while_lbl = f"WHILE_{self._while_count}"
        while_false_lbl = f"WHILE_FALSE{self._while_count}"
        self._while_count += 1
        self.writer.write_label(while_lbl)

        self.compile_expression()
        self._consume(')')

        self._consume('{')
        self.writer.write_if(while_false_lbl)

        self.compile_statements()
        self.writer.write_goto(while_lbl)
        self.writer.write_label(while_false_lbl)

        self._consume('}')

    def compile_return(self) -> None:
        """
        Compiles a return statement.
        :return: None.
        """
        self._consume('return')
        if self._get_current_token() != ';':
            self.compile_expression()
        else:
            self.writer.write_push('CONST', 0)
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

        end_lbl = f'IF_END_{self._if_count}'
        false_lbl = f'IF_FALSE_{self._if_count}'
        self._if_count += 1

        self._consume('{')
        self.writer.write_if(false_lbl)

        self.compile_statements()
        self.writer.write_goto(end_lbl)
        self.writer.write_label(false_lbl)

        self._consume('}')

        if self._get_current_token() == 'else':
            self._consume('else')
            self._consume('{')
            self.compile_statements()
            self._consume('}')

        self.writer.write_label(end_lbl)

    def compile_expression(self) -> None:
        """
        Compiles an expression.
        :return: None
        """
        self.compile_term()
        while self._get_current_token() in self.OP:
            op = self._get_current_token()
            self._consume(op)
            self.compile_term()
            if op == '*':
                self.writer.write_call('Math.multiply', 2)
            elif op == '/':
                self.writer.write_call('Math.divide', 2)
            else:
                self.writer.write_arithmetic(self.OP[op])

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
            elif self._get_current_token() == '[':
                self._consume('[')
                self.compile_expression()
                self._consume(']')

                kind = convert_kind(self.table.kind_of(curr_token))
                index = self.table.index_of(curr_token)

                self.writer.write_push(kind, index)
                self.writer.write_arithmetic('ADD')
                self.writer.write_pop('POINTER', 1)
                self.writer.write_push('THAT', 0)

            else:
                kind = convert_kind(self.table.kind_of(curr_token))
                index = self.table.index_of(curr_token)
                self.writer.write_push(kind, index)

        elif token_type == token_type.INT_CONST:
            self.writer.write_push('CONST', int(self._get_current_token()))
            self._consume(token_type)

        elif token_type == token_type.KEYWORD:
            curr_token = self._get_current_token()
            if curr_token in ['true', 'false', 'null']:
                self.writer.write_push('CONST', 0)
                if curr_token == 'true':
                    self.writer.write_arithmetic('NOT')
            if curr_token == 'this':
                self.writer.write_push('POINTER', 0)
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
                const_str = const_str.replace('"', '')

            self.writer.write_push('CONST', len(const_str.replace('"', '')))
            self.writer.write_call('String.new', 1)

            for char in const_str:
                self.writer.write_push('CONST', ord(char))
                self.writer.write_call('String.appendChar', 2)

        else:
            if self._get_current_token() == '(':
                self._consume('(')
                self.compile_expression()
                self._consume(')')
            else:
                op = self._get_current_token()
                self._consume(['-', '~'])  # unaryOp term
                self.compile_term()
                if op == '-':
                    self.writer.write_arithmetic('NEG')
                else:
                    self.writer.write_arithmetic('NOT')

    def compile_subroutine_call(self, subroutine_name=None) -> None:
        n_args = 0
        if not subroutine_name:
            subroutine_name = self._get_current_token()
            self._consume(TokenTypes.IDENTIFIER)

        if self._get_current_token() == '.':
            self._consume('.')
            sub_name = self._get_current_token()
            self._consume(TokenTypes.IDENTIFIER)
            try:  # Instance
                var_type = self.table.type_of(subroutine_name)
                kind = convert_kind(self.table.kind_of(subroutine_name))
                index = self.table.index_of(subroutine_name)
                self.writer.write_push(kind, index)
                func_name = f'{var_type}.{sub_name}'
            except KeyError:  # Class
                func_name = f'{subroutine_name}.{sub_name}'

        else:
            func_name = f'{self.class_name}.{subroutine_name}'
            n_args += 1
            self.writer.write_pop('POINTER', 0)

        self._consume('(')
        n_args += self.compile_expression_list()
        self._consume(')')

        self.writer.write_call(func_name, n_args)

    def compile_expression_list(self) -> int:
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        :return: Int. Number of arguments.
        """
        n_args = 0

        if self._get_current_token() != ')':
            self.compile_expression()
            n_args += 1
            while self._get_current_token() == ',':
                self._consume(',')
                self.compile_expression()
                n_args += 1
        return n_args

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


def str_to_kind(str_type: str) -> Kind:
    return Kind[str_type.upper()]


def convert_kind(kind: str) -> str:
    kind_mapping = {
        'VAR': 'LCL',
        'FIELD': 'THIS'
    }
    if kind in kind_mapping:
        return kind_mapping[kind]
    return kind


class CompilationEngineError(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        if self.message:
            return self.message
        else:
            return "Unexpected token. Compilation failed"
