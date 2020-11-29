import os
from enum import IntEnum
from typing import List


class VMCommandType(IntEnum):
    C_ARITHMETIC = 0
    C_PUSH = 1,
    C_POP = 2,
    C_LABEL = 3,
    C_GOTO = 4,
    C_IF = 5,
    C_FUNCTION = 6,
    C_RETURN = 7,
    C_CALL = 8


class Parser:
    def __init__(self, vm_file_path: str):
        _check_if_file_is_valid(vm_file_path)
        self.vm_code = self._sanitized_vm_file(vm_file_path)
        self.line_number = 0
        self.current_command = ''
        self._arg1 = None
        self._arg2 = None

    def has_more_commands(self) -> bool:
        """
        Are the more commands in the input?
        :return: boolean.
        """
        return len(self.vm_code) > self.line_number

    def advance(self) -> None:
        """
        Reads the next command from the input and makes it the current command. Should be called only if
        has_more_commands() is True. Initially there is no current command.
        :return: None
        """
        self.current_command = self.vm_code[self.line_number]
        self.line_number += 1

    def command_type(self) -> VMCommandType:
        """
        :return: Returns the type of the current command. VMCommandType.C_ARITHMETIC is returned for all the arithmetic/
                 logical commands.
        """
        command_parts = self.current_command.lower().split()
        c_type = None

        if self.current_command in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            self._arg1 = self.current_command
            c_type = VMCommandType.C_ARITHMETIC
        elif command_parts[0] == 'push':
            c_type = VMCommandType.C_PUSH
        elif command_parts[0] == 'pop':
            c_type = VMCommandType.C_POP

        if c_type != VMCommandType.C_ARITHMETIC:
            self._arg1 = command_parts[1]
            if c_type in [VMCommandType.C_PUSH, VMCommandType.C_POP, VMCommandType.C_FUNCTION, VMCommandType.C_CALL]:
                self._arg2 = command_parts[2]

        return c_type


    @property
    def arg1(self) -> str:
        """
        :return: Returns the first argument of the current command. In the case of C_ARITHMETIC, the command itself
                 (add, sub, etc.) is returned. Shouldn't be called if the current command is C_RETURN.
        """
        return self._arg1

    @property
    def arg2(self) -> int:
        """
        :return: Returns the second argument of the current command. Should be called only if the current command is
                 C_PUSH, C_POP, C_FUNCTION, or C_CALL.
        """
        return self._arg2

    def _sanitized_vm_file(self, path_to_vm_file) -> List[str]:
        sanitized_lines = []
        for line in self._open_file(path_to_vm_file):
            sanitized_line = self._remove_whitespace_and_comments(line)
            if sanitized_line:
                sanitized_lines.append(sanitized_line)
        return sanitized_lines

    @staticmethod
    def _open_file(path_to_vm_file) -> List[str]:
        f = open(path_to_vm_file, 'r')
        vm_code = f.readlines()
        f.close()
        return vm_code

    @staticmethod
    def _remove_whitespace_and_comments(line) -> str:
        return line.strip().split("//")[0].strip()

    def _reset(self):
        self._arg1 = None
        self._arg2 = None


def _check_if_file_is_valid(file_path: str) -> None:
    if not os.path.exists(file_path):
        raise FileNotFoundError("The File path doesn't exists")
    elif not file_path.endswith('.vm'):
        raise Exception("Unexpected file format")