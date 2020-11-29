from vm_parser import Parser, VMCommandType
from vm_code_writer import CodeWriter

import sys
from pathlib import Path

if __name__ == '__main__':
    if len(sys.argv) > 1:
        program_path = sys.argv[1]
        parser = Parser(program_path)
        file_name = Path(program_path).with_suffix('.asm')
        writer = CodeWriter(file_name)
        while parser.has_more_commands():
            parser.advance()
            c_type = parser.command_type()
            if c_type == VMCommandType.C_POP or c_type == VMCommandType.C_PUSH:
                writer.write_push_pop(c_type, parser.arg1, parser.arg2)
            elif c_type == VMCommandType.C_ARITHMETIC:
                writer.write_arithmetic(parser.arg1)
        writer.close()

    else:
        raise TypeError("1 argument is required: program path, 0 arguments entered")
