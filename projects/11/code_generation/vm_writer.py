
class VMWriter:

    def __init__(self, output_file_path: str) -> None:
        """
        Creates a new output .vm file and prepares it for writing.
        """
        self.output = open(output_file_path, 'w')

    def write_push(self, segment: str, index: int) -> None:
        """
        Writes a vm push command
        """
        pass

    def write_pop(self, segment: str, index: int) -> None:
        """
        Writes a vm pop command
        """
        pass

    def write_aritmetic(self, command: str) -> None:
        """
        Writes a VM arithmetic-logical command
        """

    def write_label(self, label: str) -> None:
        """
        Writes a VM label command
        """
        pass

    def write_goto(self, label: str) -> None:
        """
        Writes a VM goto command
        """
        pass

    def write_if(self, label: str) -> None:
        """
        Writes a VM if-goto command
        """
        pass

    def write_call(self, name: str, number_args: int) -> None:
        """
        Writes a VM call command
        """
        pass

    def write_function(self, name: str, number_locals: int) -> None:
        """
        Writes a VM function command
        """
        pass

    def write_return(self) -> None:
        """
        Write a VM return command
        """
        pass

    def close(self) -> None:
        """
        Closes the output file.
        """
        self.output.close()