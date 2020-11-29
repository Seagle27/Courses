import os
from vm_parser import VMCommandType


class CodeWriter:
    memory_prefixes = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

    def __init__(self, file_name: str):
        self.output_file = open(file_name, 'w+')
        self._file_name = file_name
        self._bool_counter = 0

    def write_arithmetic(self, command: str) -> None:
        """
        Writes to the output file the assembly code that implements the given arithmetic command.
        :param command: str. VM arithmetic command (like add, sub, lt, gt, etc.)
        :return: None
        """
        self.output_file.write(f"//{command}\n")
        if command in ['neg', 'not']:
            self.output_file.write(self._decrement_sp())
        else:
            self._pop_stack_to_d()

        if command == 'add':
            self.output_file.writelines(['A=A-1\n', 'M=M+D\n'])
        elif command == 'sub':
            self.output_file.writelines(['A=A-1\n', 'M=M-D\n'])
        elif command == 'neg':
            self.output_file.writelines(['A=M\n', 'M=-M\n'])
        elif command in ['eq', 'gt', 'lt']:
            # -1 = True, 0 = False
            self.output_file.writelines(['A=A-1\n', 'D=M-D\n', 'M=-1\n', f"@EQ-{self._bool_counter}\n"])
            self.output_file.write(f'D;J{command.upper()}\n')  # JEQ / JGT / JLT
            self.output_file.write(self.go_to_sp_addr())
            self.output_file.writelines(['A=A-1\n', 'M=0\n', f"(@{command.upper()}-{self._bool_counter})\n"])
            self._bool_counter += 1
        elif command == 'and':
            self.output_file.writelines(['A=A-1\n', 'M=D&M\n'])
        elif command == 'or':
            self.output_file.writelines(['A=A-1\n', 'M=D|M\n'])
        elif command == 'not':
            self.output_file.writelines(['A=M\n', 'M=!M\n'])
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
        self.output_file.write(f"//{command.name} {segment} {index}\n")
        if command == VMCommandType.C_PUSH:

            if segment in ['local', 'argument', 'this', 'that']:
                self.output_file.writelines([f"@{CodeWriter.memory_prefixes[segment]}\n", "D=M\n", f"@{index}\n",
                                             "A=A+D\n", "D=M\n"])
            elif segment == "constant":
                self.output_file.writelines([f"@{index}\n", "D=M\n"])
            elif segment == "temp":
                self.output_file.writelines(['@5\n', 'D=A\n', f'@{index}\n', 'A=A+D\n', 'D=M\n'])
            elif segment == 'static':
                self.output_file.writelines([f'@{self._file_name}.{index}\n', 'D=M\n'])
            elif segment == 'pointer':
                pointer = 'THAT' if index else 'THIS'  # index 0 = THIS, index 1 = THAT
                self.output_file.writelines([f'@{pointer}\n', 'D=A\n'])
            else:
                raise ValueError(f"{segment} is unsupported.")

            self._push_d_to_stack()

        elif command == VMCommandType.C_POP:
            if segment in ['local', 'argument', 'this', 'that']:
                self.output_file.writelines([f"@{CodeWriter.memory_prefixes[segment]}\n", "D=M\n", f"@{index}\n",
                                             "A=A+D\n", "D=M\n"])
            elif segment == "temp":
                self.output_file.writelines(['@5\n', 'D=A\n', f'@{index}\n', 'A=A+D\n', 'D=M\n'])
            elif segment == 'static':
                self.output_file.writelines([f'@{self._file_name}.{index}\n', 'D=M\n'])
            elif segment == 'pointer':
                pointer = 'THAT' if index else 'THIS'  # index 0 = THIS, index 1 = THAT
                self.output_file.writelines([f'@{pointer}\n', 'D=A\n'])
            else:
                raise ValueError(f"{segment} is unsupported.")

            self._pop_stack_to_d()

        else:
            raise ValueError(f"{command} is unsupported. Only C_PUSH and C_POP commands are allowed")

    def _push_d_to_stack(self) -> None:
        """Push from D onto top of stack, increment @SP"""
        self.output_file.write(self._update_sp_value())
        self.output_file.write(self._increment_sp())

    def _pop_stack_to_d(self) -> None:
        """Decrement @SP, pop from top of stack onto D"""
        self.output_file.write(self._decrement_sp())
        self.output_file.writelines(['A=M\n', 'D=M\n'])

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
