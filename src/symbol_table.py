class SymbolTable:
    def __init__(self, name, subroutine_type=None, return_type=None, jack_class=None):
        self.name = name
        self.jack_class = jack_class
        self.subroutine_type = subroutine_type
        self.return_type = return_type
        self.symbols = {}
        self.field_symbols = 0
        self.static_symbols = 0
        self.arg_symbols = 0
        self.var_symbols = 0

        if subroutine_type == 'method':
            self.add_arg('this', self.jack_class.name)

    def add_field(self, name, var_type):
        self.symbols[name] = ('field', var_type, self.field_symbols)
        self.field_symbols += 1

    def add_static(self, name, var_type):
        self.symbols[name] = ('static', var_type, self.static_symbols)
        self.static_symbols += 1

    def add_arg(self, name, var_type):
        self.symbols[name] = ('arg', var_type, self.arg_symbols)
        self.arg_symbols += 1

    def add_var(self, name, var_type):
        self.symbols[name] = ('var', var_type, self.var_symbols)
        self.var_symbols += 1

    def get_class_symbol(self, name):
        return self.symbols.get(name)

    def get_subroutine_symbol(self, name):
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol
        return self.jack_class.get_class_symbol(name)
