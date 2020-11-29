from vm_parser import VMCommandType
from functools import singledispatchmethod
from datetime import datetime as dt


class CodeWriter:
    memory_prefixes = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

    def __init__(self, file_name: str):
        self.output_file = open(file_name, 'w+')
        self._file_name = file_name
        self._bool_counter = 0
        self._call_counter = 0
        self.write_init()

    def set_file_name(self, file_name: str) -> None:
        """
        Call whenever the translation of a new VM file has started.
        :param file_name: str. Name of the new file name.
        :return: None
        """
        self._file_name = file_name
        self._write(f'// Current file is: {file_name}')

    def write_init(self):
        self._write(['@256', 'D=A', '@SP', 'M=D'])
        self.write_call('Sys.init', 0)

    def write_arithmetic(self, command: str) -> None:
        """
        Writes to the output file the assembly code that implements the given arithmetic command.
        :param command: str. VM arithmetic command (like add, sub, lt, gt, etc.)
        :return: None
        """
        self._write(f"//{command}\n")
        if command in ['neg', 'not']:
            self._write(self._decrement_sp())
        else:
            self._pop_stack_to_d()

        if command == 'add':
            self._write(['A=A-1', 'M=M+D'])
        elif command == 'sub':
            self._write(['A=A-1', 'M=M-D'])
        elif command == 'neg':
            self._write(['A=M', 'M=-M'])
        elif command in ['eq', 'gt', 'lt']:
            # -1 = True, 0 = False
            self._write(['A=A-1', 'D=M-D', 'M=-1', f"@EQ-{self._bool_counter}"])
            self._write(f'D;J{command.upper()}')  # JEQ / JGT / JLT
            self._write(self.go_to_sp_addr())
            self._write(['A=A-1', 'M=0', f"(@{command.upper()}-{self._bool_counter})"])
            self._bool_counter += 1
        elif command == 'and':
            self._write(['A=A-1', 'M=D&M'])
        elif command == 'or':
            self._write(['A=A-1', 'M=D|M'])
        elif command == 'not':
            self._write(['A=M', 'M=!M'])
        else:
            raise ValueError(f"{command} command is unsupported.")

    def write_push_pop(self, command: VMCommandType.C_PUSH or VMCommandType.C_POP, segment: str, index: int) -> None:
        """
        Writes to the output file the assembly code that implements the given command, where command is either C_PUSH
        or C_POP
        :param command: VMCommandType.C_PUSH or VMCommandType.C_POP
        :param segment: str. On which memory segment to operate
        :param index: Memory segment index to operate on.
        :return: None
        """
        index = str(index)
        self._write(f"//{command.name} {segment} {index}")
        if command == VMCommandType.C_PUSH:

            if segment in ['local', 'argument', 'this', 'that']:
                self._write([f"@{CodeWriter.memory_prefixes[segment]}", "D=M", f"@{index}",
                             "A=A+D", "D=M"])
            elif segment == "constant":
                self._write([f"@{index}", "D=M"])
            elif segment == "temp":
                self._write(['@5', 'D=A', f'@{index}', 'A=A+D', 'D=M'])
            elif segment == 'static':
                self._write([f'@{self._file_name}.{index}', 'D=M'])
            elif segment == 'pointer':
                pointer = 'THAT' if index else 'THIS'  # index 0 = THIS, index 1 = THAT
                self._write([f'@{pointer}', 'D=A'])
            else:
                raise ValueError(f"{segment} is unsupported.")

            self._push_d_to_stack()

        elif command == VMCommandType.C_POP:
            if segment in ['local', 'argument', 'this', 'that']:
                self._write([f"@{CodeWriter.memory_prefixes[segment]}", "D=M", f"@{index}",
                             "A=A+D", "D=M"])
            elif segment == "temp":
                self._write(['@5', 'D=A', f'@{index}', 'A=A+D', 'D=M'])
            elif segment == 'static':
                self._write([f'@{self._file_name}.{index}', 'D=M'])
            elif segment == 'pointer':
                pointer = 'THAT' if index else 'THIS'  # index 0 = THIS, index 1 = THAT
                self._write([f'@{pointer}', 'D=A'])
            else:
                raise ValueError(f"{segment} is unsupported.")

            self._pop_stack_to_d()

        else:
            raise ValueError(f"{command} is unsupported. Only C_PUSH and C_POP commands are allowed")

    def write_label(self, label: str) -> None:
        """
        Writes assembly code that effects the label command
        :return: None
        """
        self._write(f'({self._file_name}${label})')

    def write_goto(self, label: str) -> None:
        """
        Writes assembly code that jumps to the entered label
        :param label: label to go to
        :return: None
        """
        self._write(f'@{self._file_name}${label}')
        self._write('0;JMP')

    def write_if(self, label: str) -> None:
        """
        If cond (top element on stack) jump to execute the
        command just after label.
        :return: None
        """
        self._pop_stack_to_d()
        self._write(f'@{self._file_name}${label}')
        self._write('D;JNE')

    def write_call(self, function_name: str, num_args: int) -> None:
        """
        Writes assembly code that calls the desired function
        :param function_name: Which function to call
        :param num_args: The amount of arguments that have been pushed onto the stack
        :return: None
        """
        ret_addr = function_name+f'&ret.{self._call_counter}'  # Unique return address
        self._call_counter += 1
        self._write([f'@{ret_addr}', 'D=A'])
        self._push_d_to_stack()  # Push return address to stack

        for addr in CodeWriter.memory_prefixes.values():  # Push LCL, ARG, THIS, THAT onto the stack
            self._write([f'@{addr}', 'D=M'])
            self._push_d_to_stack()

        self._write(['@SP', 'D=M', f'@{CodeWriter.memory_prefixes["local"]}', 'M=D'])  # LCL = SP
        self._write([f'@{5+num_args}', 'D=D-A', f'@{CodeWriter.memory_prefixes["argument"]}', 'M=D'])  # LCL = SP,
        # can be done because at this point D is already SP.

        self.write_goto(function_name)
        self.write_label(ret_addr)

    def write_function(self, function_name: str, num_variables: int) -> None:
        """
        Writes assembly code that handles setting up of a function's execution
        :param function_name: The name of the function
        :param num_variables: The amount of the function's local variables
        :return: None
        """
        self.write_label(function_name)
        for _ in range(num_variables):
            self._write('D=0')
            self._push_d_to_stack()

    def write_return(self) -> None:
        """
        Writes assembly code that moves the return value to the caller, reinstates the caller's state, and then goes to
        the caller's return address.
        :return: None
        """
        end_frame = 'R13'
        ret_address = 'R14'

        self._write(['@'+CodeWriter.memory_prefixes["local"], "D=M", '@'+end_frame, "M=D"])  # end_frame = LCL
        self._write(['@5', 'D=D-A', 'A=D', 'D=M', '@'+ret_address, 'M=D'])  # get the caller's return
        # address and save it in ret_address
        self._pop_stack_to_d()
        self._write(['@'+CodeWriter.memory_prefixes['argument'], 'A=M', 'M=D'])  # *ARG = pop()
        self._write(['@'+CodeWriter.memory_prefixes['argument'], 'D=M', '@SP', 'M=D'])  # SP = ARG + 1

        for i, addr in enumerate(['@THAT', '@THIS', '@ARG', '@LCL']):  # Restores THAT, THIS, ARG and LCL of the caller
            self._write(['@' + end_frame, 'D=M'])
            self._write([f'@{i+1}', 'D=D-A', addr, 'D=M'])

        self._write(['@'+ret_address, 'A=M', '0;JMP'])  # goto ret_address

    @singledispatchmethod
    def _write(self, message) -> None:
        print("1")

    @_write.register
    def _(self, message: str) -> None:
        message = message + '\n' if not message.endswith('\n') else message
        self.output_file.write(message)

    @_write.register
    def _(self, message: list) -> None:
        message = [item + '\n' for item in message]
        self.output_file.writelines(message)

    def _push_d_to_stack(self) -> None:
        """Push from D onto top of stack, increment @SP"""
        self._write(self._update_sp_value())
        self._write(self._increment_sp())

    def _pop_stack_to_d(self) -> None:
        """Decrement @SP, pop from top of stack onto D"""
        self._write(self._decrement_sp())
        self._write(['A=M', 'D=M'])

    @staticmethod
    def _increment_sp() -> str:
        return "@SP\nM=M+1\n"

    @staticmethod
    def _decrement_sp() -> str:
        return "@SP\nM=M-1\n"

    @staticmethod
    def _update_sp_value() -> str:
        return '@SP\nA=M\nM=D\n'

    @staticmethod
    def go_to_sp_addr() -> str:
        return '@SP\nA=M\n'

    def close(self) -> None:
        self.output_file.close()
