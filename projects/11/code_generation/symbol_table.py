from enum import IntEnum


class Kind(IntEnum):
    STATIC = 0
    FIELD = 1
    ARG = 2
    VAR = 3


class SymbolTable:
    def __init__(self):
        self.class_table = dict()
        self.subroutine_table = dict()

    def define(self, name: str, var_type: str, kind: Kind) -> None:
        """
        Defines a new identifier of the given name, type, and kind and assigns it a running index.
        STATIC and FIELD identifiers have a class scope, while ARG and VAR identifiers have a subroutine scope.
        :return: None.
        """
        pass

    def var_count(self, kind: Kind) -> int:
        """
        Returns the number of variables of the given kind already defined in the current scope.
        """
        pass

    def kind_of(self, name: str) -> Kind:
        """
        Returns the kind of the named identifier in the current scope. If the identifier is unknown in the current
        scope, returns None.
        """
        pass

    def type_of(self, name: str) -> str:
        """
        Returns the type of the named identifier in the current scope.
        """
        pass

    def index_of(self, name: str) -> int:
        """
        Return the index assigned to the named identifier.
        """
        pass
