import os
from enum import Enum
import sys
from itertools import tee

comp_dict = {'0': '0101010', '1': '0111111', '-1': '0111010', 'D': '0001100', 'A': '0110000',
             '!D': '0001101', '!A': '0110001', '-D': '0001111', '-A': '0110011',
             'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110', 'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011',
             'A-D': '0000111', 'D&A': '0000000', 'D|A': '0010101', 'M': '1110000', '!M': '1110001', '-M': '1110011',
             'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010', 'D-M': '1010011', 'M-D': '1000111', 'D&M': '1000000',
             'D|M': '1010101'
             }

dest_dict = {'null': '000', 'M': '001', 'D': '010', 'MD': '011', 'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}

jump_dict = {'null': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011', 'JLT': '100', 'JNE': '101', 'JLE': '110',
             'JMP': '111'}

symbol_dict = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5,
               'R6': 6, 'R7': 7, 'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
               'SCREEN': 16384, 'KBD': 24576}


class InstructionType(Enum):
    A = 0
    C = 1
    L = 2


class Parser:
    def __init__(self, asm_file_path: str):
        self.variable_pointer = 16
        self._check_if_file_is_valid(asm_file_path)
        file_name = asm_file_path.split('.')[0]
        self.program_output = open(f"{file_name}.hack", 'w+')
        self.scan_labels(asm_file_path)
        self.parse_file(asm_file_path)

    def scan_labels(self, file_path: str) -> None:
        first_iter = self.get_next_command(file_path)
        try:
            command_counter = 0
            for command in first_iter:
                command_type = self.command_type(command)
                if command_type == InstructionType.L:
                    global symbol_dict
                    symbol_dict[command.strip('()')] = command_counter
                else:
                    command_counter += 1

        except StopIteration:
            pass

    def parse_file(self, file_path: str) -> None:
        commands_generator = self.get_next_command(file_path)
        try:
            for i, command in enumerate(commands_generator):
                command_type = self.command_type(command)

                if command_type == InstructionType.A:
                    self.program_output.write(self.parse_a_command(command) + '\n')
                elif command_type == InstructionType.C:
                    self.program_output.write(self.parse_c_command(command) + '\n')
        except StopIteration:
            pass

    def parse_a_command(self, command):
        """
       Parses the received A instruction and translates it into 16 bit binary commands
       :param command: Valid A instruction (Str.)
       :return: 16 bit binary representation of the received command
       """
        global symbol_dict

        address = command.split('@')[1]
        if address.isdigit():
            pass
        elif address in symbol_dict:
            address = symbol_dict[address]
        else:
            symbol_dict[address] = self.variable_pointer
            self.variable_pointer += 1
            address = symbol_dict[address]

        return f'0{int(address):015b}'

    @staticmethod
    def parse_c_command(command):
        """
        Parses the received C instruction and translates it into 16 bit binary commands
        :param command: Valid C instruction (Str.)
        :return: 16 bit binary representation of the received command
        """
        const = '111'
        if '=' in command:
            parts = command.split('=')
            dest = dest_dict[parts[0]]
            comp = comp_dict[parts[1]]
            jump = jump_dict[command.split(';')[1] if ';' in command else 'null']
        else:
            dest = dest_dict['null']
            parts = command.split(';')
            comp = comp_dict[parts[0]]
            jump = jump_dict[parts[1]]
        return const + comp + dest + jump

    @staticmethod
    def get_next_command(file_path: str):
        with open(file_path, 'r') as file:
            data = file.readlines()
        for line in data:
            command = ''.join(line.partition('/')[0].split())
            if command:
                yield command

    @staticmethod
    def _check_if_file_is_valid(file_path: str) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError("The File path doesn't exists")
        elif not file_path.endswith('.asm'):
            raise Exception("Unexpected file format")

    @staticmethod
    def command_type(command):
        if command.startswith('@'):
            if command.split('@')[1]:  # a instruction
                return InstructionType.A
        elif command.startswith('('):
            return InstructionType.L
        else:  # c command
            return InstructionType.C


if __name__ == '__main__':
    if len(sys.argv) > 1:
        program_path = sys.argv[1]
        Parser(program_path)
    else:
        raise Exception("Please enter the program path")
