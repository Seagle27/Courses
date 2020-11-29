from vm_parser import Parser, VMCommandType
from vm_code_writer import CodeWriter

import sys
from pathlib import Path, PurePath
from os.path import isfile, isdir, join
import glob

if __name__ == '__main__':
    if len(sys.argv) > 1:
        program_path = sys.argv[1]
        if isfile(program_path):
            files = [program_path]
            output_path = Path(program_path).parent
        elif isdir(program_path):
            files = glob.glob(join(program_path, '*.vm'))
            output_path = program_path
        else:
            raise FileNotFoundError("[Errno 2] No such file or directory: ", program_path)

        output_file_name = PurePath(program_path).name.split('.')[0] + '.asm'
        output_file = Path(output_path, output_file_name)
        writer = CodeWriter(output_file)

        for i, vm_file in enumerate(files):
            parser = Parser(vm_file)
            file_name = PurePath(program_path).name
            writer.set_file_name(file_name)
            while parser.has_more_commands():
                parser.advance()
                c_type = parser.command_type()
                if c_type == VMCommandType.C_POP or c_type == VMCommandType.C_PUSH:
                    writer.write_push_pop(c_type, parser.arg1, parser.arg2)
                elif c_type == VMCommandType.C_ARITHMETIC:
                    writer.write_arithmetic(parser.arg1)
                elif c_type == VMCommandType.C_LABEL:
                    writer.write_label(parser.arg1)
                elif c_type == VMCommandType.C_GOTO:
                    writer.write_goto(parser.arg1)
                elif c_type == VMCommandType.C_IF:
                    writer.write_if(parser.arg1)
                elif c_type == VMCommandType.C_FUNCTION:
                    writer.write_function(parser.arg1, int(parser.arg2))
                elif c_type == VMCommandType.C_CALL:
                    writer.write_call(parser.arg1, int(parser.arg2))
                elif c_type == VMCommandType.C_RETURN:
                    writer.write_return()
        writer.close()

    else:
        raise TypeError("1 argument is required: program path, 0 arguments entered")
