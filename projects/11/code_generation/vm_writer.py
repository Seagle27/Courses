
class VMWriter:

    def __init__(self, output_file_path: str) -> None:
        """
        Creates a new output .vm file and prepares it for writing.
        """
        self.output = open(output_file_path, 'w')
        self._memory_segments = {"LCL": "local", "ARG": "argument", "CONST": "constant", "FIELD": "this"}
        self._memory_segments.update({key: key.lower() for key in ['POINTER', 'STATIC', 'THIS', 'THAT', 'TEMP']})

    def write_push(self, segment: str, index: int) -> None:
        """
        Writes a vm push command
        """
        segment = self._memory_segments[segment]
        self._write(f'push {segment} {index}')

    def write_pop(self, segment: str, index: int) -> None:
        """
        Writes a vm pop command
        """
        segment = self._memory_segments[segment]
        self._write(f'pop {segment} {index}')

    def write_arithmetic(self, command: str) -> None:
        """
        Writes a VM arithmetic-logical command
        """
        if command not in ('ADD', 'SUB', 'NEG', 'EQ', 'GT',
                           'LT', 'AND', 'OR', 'NOT'):
            raise TypeError(f'{command} not supported.')

        self._write(command.lower())

    def write_label(self, label: str) -> None:
        """
        Writes a VM label command
        """
        self._write(f'label {label}')

    def write_goto(self, label: str) -> None:
        """
        Writes a VM goto command
        """
        self._write(f'goto {label}')

    def write_if(self, label: str) -> None:
        """
        Writes a VM if-goto command
        """
        self._write(f'if-goto {label}')

    def write_call(self, name: str, number_args: int) -> None:
        """
        Writes a VM call command
        """
        self._write(f'call {name} {str(number_args)}')

    def write_function(self, name: str, number_locals: int) -> None:
        """
        Writes a VM function command
        """
        self._write(f'function {name} {str(number_locals)}')

    def write_return(self) -> None:
        """
        Write a VM return command
        """
        self._write('return')

    def close(self) -> None:
        """
        Closes the output file.
        """
        self.output.close()

    def _write(self, cmd: str):
        self.output.write(cmd+'\n')