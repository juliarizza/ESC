"""
    - The symbol table abstraction can be implemented using two
    separated hash tables: one for the class scope, and one for
    the subroutine scope.
    - When we start compiling a new subroutine, the latter hash
    table can be reset.
    - When compiling an error-free code, each symbol not found
    in the symbol tables can be assumed to be either a subroutine
    name or a class name.
"""

class SymbolTable():
    KINDS = {
        "var": "local",
        "argument": "argument",
        "field": "this",
        "static": "static"
    }

    def __init__(self):
        """
            Creates a new symbol table.
        """
        self.class_scope = []
        self.subroutine_scope = []

    def startSubroutine(self):
        """
            Starts a new subroutine scope.
            (i.e., resets the subroutine's
            symbol table).
        """
        self.subroutine_scope = []

    def define(self, name, type, kind):
        """
            Defines a new identifier of the given
            name, type, and kind, and assigns it a
            running index. STATIC and FIELD identifiers
            have a class scope, while ARG and VAR
            identifiers have a subroutine scope.
        """
        if kind == "static" or kind == "field":
            self.class_scope.append(
                {
                    "name": name, "type": type,
                    "kind": self.KINDS[kind],
                    "index": self.varCount(self.KINDS[kind])
                }
            )
        elif kind == "argument" or kind == "var":
            self.subroutine_scope.append(
                {
                    "name": name, "type": type,
                    "kind": self.KINDS[kind],
                    "index": self.varCount(self.KINDS[kind])
                }
            )

    def varCount(self, kind):
        """
            Returns the number of variables of the
            given kind already defined in the current
            scope.
        """
        scope = self.class_scope + self.subroutine_scope
        same_kind_items = [k for k in scope if k["kind"] == kind]
        return len(same_kind_items)

    def kindOf(self, name):
        """
            Returns the kind of the named identifier
            in the current scope. If the identifier
            is unknown in the current scope, returns
            NONE.
        """
        scope = self.class_scope + self.subroutine_scope
        named_items = [n for n in scope if n["name"] == name]
        return named_items[0]["kind"] if len(named_items) else None

    def typeOf(self, name):
        """
            Returns the type of the named identifier
            in the current scope.
        """
        scope = self.class_scope + self.subroutine_scope
        named_items = [n for n in scope if n["name"] == name]
        return named_items[0]["type"] if len(named_items) else None

    def indexOf(self, name):
        """
            Returns the index assigned to the named
            identifier.
        """
        scope = self.class_scope + self.subroutine_scope
        named_items = [n for n in scope if n["name"] == name]
        return named_items[0]["index"] if len(named_items) else None
