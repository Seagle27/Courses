from enum import IntEnum


class Kind(IntEnum):
    STATIC = 0
    FIELD = 1
    ARG = 2
    VAR = 3


class SymbolTable(dict):
    """
    A hashtable to perform variable lookup.
    """
    def __init__(self):
        super().__init__()
        self.class_table = dict()
        self.subroutine_table = dict()
        self._count = {kind.name: 0 for kind in Kind}

    def define(self, name: str, var_type: str, kind: Kind) -> None:
        """
        Defines a new identifier of the given name, type, and kind and assigns it a running index.
        STATIC and FIELD identifiers have a class scope, while ARG and VAR identifiers have a subroutine scope.
        :return: None.
        :Raises: TypeError: If the kind of given variable is invalid
        """
        try:
            i = self._count[kind.name]
        except KeyError:
            raise TypeError('{} is not a supported kind.'.format(kind.name))

        if kind in [Kind.STATIC, Kind.FIELD]:
            self.class_table[name] = {'type': var_type, 'kind': kind.name, 'index': i}
        else:  # kind in [Kind.ARG, Kind.VAR]:
            self.subroutine_table[name] = {'type': var_type, 'kind': kind.name, 'index': i}

        self._count[kind.name] += 1

    def var_count(self, kind: Kind) -> int:
        """
        Returns the number of variables of the given kind already defined in the current scope.
        """
        return self._count[kind.name]

    def kind_of(self, name: str) -> str:
        """
        Returns the kind of the named identifier in the current scope. If the identifier is unknown in the current
        scope, raise an KeyError exception.
        """
        return self.get(name)['kind']

    def type_of(self, name: str) -> str:
        """
        Returns the type of the named identifier in the current scope.
        """
        return self.get(name)['type']

    def index_of(self, name: str) -> int:
        """
        Return the index assigned to the named identifier.
        """
        return self.get(name)['index']

    def reset(self):
        """
        Clears the subroutine table.
        """
        self.subroutine_table.clear()
        self._count['ARG'] = 0
        self._count['VAR'] = 0

    def get(self, key):
        ret = self[key]
        return ret

    def __getitem__(self, key):
        if key in self.subroutine_table:
            return self.subroutine_table[key]
        elif key in self.class_table:
            return self.class_table[key]
        else:
            raise KeyError(f"{key} not in any scope.")
