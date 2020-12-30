import glob
import sys
from pathlib import Path, PurePath
from os.path import isfile, isdir, join

from jack_tokenizer import JackTokenizer
from compilation_engine import CompilationEngine


if __name__ == '__main__':
    if len(sys.argv) > 1:
        program_path = sys.argv[1]
        if isfile(program_path):
            files = [program_path]
            output_path = Path(program_path).parent
        elif isdir(program_path):
            files = glob.glob(join(program_path, '*.jack'))
            output_path = program_path
        else:
            raise FileNotFoundError("[Errno 2] No such file or directory: ", program_path)

        output_file_name = PurePath(program_path).name.split('.')[0] + '.xml'
        output_file = Path(output_path, output_file_name)

        for file in files:
            file_tokenizer = JackTokenizer(file)
            CompilationEngine(file_tokenizer, output_file)

    else:
        raise TypeError("1 argument is required: program path, 0 arguments entered")
