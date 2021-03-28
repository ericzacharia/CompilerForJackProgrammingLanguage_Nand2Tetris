from vm_writer import VMWriter
from symbol_table import SymbolTable


class CompilationEngine:
    """Compiles a jack source file from a jack tokenizer into xml form in output_file"""

    num_labels = 0
    operators_dict = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2', '/': 'call Math.divide 2', '&': 'and',
                      '|': 'or', '<': 'lt', '>': 'gt', '=': 'eq'}

    def __init__(self, tokenizer, output_file):
        """Instantiates an object of the CompilationEngine Class"""
        self.tokenizer = tokenizer
        self.vm_writer = VMWriter(output_file)

    def compile_statement(self, jack_subroutine):
        """Compiles a sequence of statements, not including the enclosing “{}”."""
        has_more_tokens = True
        while has_more_tokens:
            token = self.tokenizer.current_token()

            if token == ('keyword', 'if'):
                self.tokenizer.advance()
                self.tokenizer.advance()
                self.compile_expression(jack_subroutine)
                self.tokenizer.advance()
                self.tokenizer.advance()
                false_label = CompilationEngine.get_label()
                end_label = CompilationEngine.get_label()
                self.vm_writer.write_if_goto(false_label)
                self.compile_statement(jack_subroutine)
                self.vm_writer.write_goto(end_label)
                self.vm_writer.write_label(false_label)
                self.tokenizer.advance()
                token = self.tokenizer.current_token()

                if token == ('keyword', 'else'):
                    self.tokenizer.advance()
                    self.tokenizer.advance()
                    self.compile_statement(jack_subroutine)
                    self.tokenizer.advance()
                self.vm_writer.write_label(end_label)
            elif token == ('keyword', 'while'):
                self.tokenizer.advance()
                self.tokenizer.advance()
                while_label = CompilationEngine.get_label()
                false_label = CompilationEngine.get_label()
                self.vm_writer.write_label(while_label)
                self.compile_expression(jack_subroutine)
                self.tokenizer.advance()
                self.tokenizer.advance()
                self.vm_writer.write_if_goto(false_label)
                self.compile_statement(jack_subroutine)
                self.vm_writer.write_goto(while_label)
                self.vm_writer.write_label(false_label)
                self.tokenizer.advance()
            elif token == ('keyword', 'let'):
                self.tokenizer.advance()
                var_name = self.tokenizer.advance()[1]
                jack_symbol = jack_subroutine.get_subroutine_symbol(var_name)

                if self.tokenizer.current_token()[1] == '[':
                    self.tokenizer.advance()
                    self.compile_expression(jack_subroutine)
                    self.tokenizer.advance()
                    self.tokenizer.advance()
                    self.vm_writer.write_push_symbol(jack_symbol)
                    self.vm_writer.write('add')
                    self.compile_expression(jack_subroutine)
                    self.vm_writer.write_pop('temp', 0)
                    self.vm_writer.write_pop('pointer', 1)
                    self.vm_writer.write_push('temp', 0)
                    self.vm_writer.write_pop('that', 0)
                else:
                    self.tokenizer.advance()
                    self.compile_expression(jack_subroutine)
                    self.vm_writer.write_pop_symbol(jack_symbol)
                self.tokenizer.advance()
            elif token == ('keyword', 'do'):
                self.tokenizer.advance()
                self.compile_term(jack_subroutine)
                self.vm_writer.write_pop('temp', 0)
                self.tokenizer.advance()
            elif token == ('keyword', 'return'):
                self.tokenizer.advance()
                token = self.tokenizer.current_token()

                if token != ('symbol', ';'):
                    self.compile_expression(jack_subroutine)
                else:
                    self.vm_writer.write_constant(0)
                self.vm_writer.write_return()
                self.tokenizer.advance()
            else:
                has_more_tokens = False

    def compile_class(self):
        """Compiles a complete class."""
        self.tokenizer.advance()
        class_name = self.tokenizer.advance()[1]
        jack_class = SymbolTable(class_name)
        self.tokenizer.advance()
        self.compile_class_var_dec(jack_class)
        self.compile_subroutine(jack_class)
        self.tokenizer.advance()

    def compile_class_var_dec(self, jack_class):
        """Compiles a static declaration or a field declaration."""
        token = self.tokenizer.current_token()
        while token is not None and token[0] == 'keyword' and token[1] in ['static', 'field']:
            self.tokenizer.advance()
            is_static = token[1] == 'static'
            var_type = self.tokenizer.advance()[1]
            still_vars = True

            while still_vars:
                var_name = self.tokenizer.advance()[1]
                if is_static:
                    jack_class.add_static(var_name, var_type)
                    jack_class.add_static(var_name, var_type)
                else:
                    jack_class.add_field(var_name, var_type)
                token = self.tokenizer.advance()
                still_vars = token == ('symbol', ',')

            token = self.tokenizer.current_token()

    def compile_subroutine(self, jack_class):
        """Compiles a complete method, function, or constructor"""
        token = self.tokenizer.current_token()

        while token is not None and token[0] == 'keyword' and token[1] in ['constructor', 'function', 'method']:
            subroutine_type = self.tokenizer.advance()[1]
            return_type = self.tokenizer.advance()[1]
            name = self.tokenizer.advance()[1]
            jack_subroutine = SymbolTable(name, subroutine_type, return_type, jack_class)
            self.tokenizer.advance()
            self.compile_parameter_list(jack_subroutine)
            self.tokenizer.advance()
            self.tokenizer.advance()
            token = self.tokenizer.current_token()

            while token is not None and token == ('keyword', 'var'):
                self.tokenizer.advance()
                var_type = self.tokenizer.advance()[1]
                var_name = self.tokenizer.advance()[1]
                jack_subroutine.add_var(var_name, var_type)

                while self.tokenizer.advance()[1] == ',':
                    var_name = self.tokenizer.advance()[1]
                    jack_subroutine.add_var(var_name, var_type)
                token = self.tokenizer.current_token()
            self.vm_writer.write_function(jack_subroutine)

            if jack_subroutine.subroutine_type == 'constructor':
                field_count = jack_subroutine.jack_class.field_symbols
                self.vm_writer.write_push('constant', field_count)
                self.vm_writer.write_call('Memory', 'alloc', 1)
                self.vm_writer.write_pop('pointer', 0)
            elif jack_subroutine.subroutine_type == 'method':
                self.vm_writer.write_push('argument', 0)
                self.vm_writer.write_pop('pointer', 0)

            self.compile_statement(jack_subroutine)
            self.tokenizer.advance()
            token = self.tokenizer.current_token()

    def compile_parameter_list(self, jack_subroutine):
        """Compiles a (possibly empty) parameter list, not including the enclosing “()”."""
        token = self.tokenizer.current_token()
        still_vars = token is not None and token[0] in ['keyword', 'identifier']
        while still_vars:
            token = self.tokenizer.advance()
            param_type = token[1]
            param_name = self.tokenizer.advance()[1]
            jack_subroutine.add_arg(param_name, param_type)
            token = self.tokenizer.current_token()
            if token == ('symbol', ','):
                self.tokenizer.advance()
                token = self.tokenizer.current_token()
                still_vars = token is not None and token[0] in ['keyword', 'identifier']
            else:
                still_vars = False

    def compile_expression(self, jack_subroutine):
        """Compiles an expression"""
        self.compile_term(jack_subroutine)
        token = self.tokenizer.current_token()

        while token[1] in '+-*/&|<>=':
            binary_op = self.tokenizer.advance()[1]
            self.compile_term(jack_subroutine)
            self.vm_writer.write(CompilationEngine.operators_dict[binary_op])
            token = self.tokenizer.current_token()

    def compile_term(self, jack_subroutine):
        """Compiles a term. If the current token is an identifier, this method distinguishes between a variable,
        an array entry, and a subroutine call."""
        token = self.tokenizer.advance()

        if token[1] in ['-', '~']:
            self.compile_term(jack_subroutine)

            if token[1] == '-':
                self.vm_writer.write('neg')
            elif token[1] == '~':
                self.vm_writer.write('not')
        elif token[1] == '(':
            self.compile_expression(jack_subroutine)
            self.tokenizer.advance()
        elif token[0] == 'integerConstant':
            self.vm_writer.write_constant(token[1])
        elif token[0] == 'stringConstant':
            self.vm_writer.write_string(token[1])
        elif token[0] == 'keyword':

            if token[1] == 'this':
                self.vm_writer.write_push('pointer', 0)
            else:
                self.vm_writer.write_constant(0)

                if token[1] == 'true':
                    self.vm_writer.write('not')
        elif token[0] == 'identifier':
            token_value = token[1]
            token_var = jack_subroutine.get_subroutine_symbol(token_value)
            token = self.tokenizer.current_token()

            if token[1] == '[':
                self.tokenizer.advance()
                self.compile_expression(jack_subroutine)
                self.vm_writer.write_push_symbol(token_var)
                self.vm_writer.write('add')
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)
                self.tokenizer.advance()
            else:
                func_name = token_value
                func_class = jack_subroutine.jack_class.name
                default_call = True
                arg_count = 0

                if token[1] == '.':
                    default_call = False
                    self.tokenizer.advance()
                    func_obj = jack_subroutine.get_subroutine_symbol(token_value)
                    func_name = self.tokenizer.advance()[1]

                    if func_obj:
                        func_class = token_var[1]
                        arg_count = 1
                        self.vm_writer.write_push_symbol(token_var)
                    else:
                        func_class = token_value
                    token = self.tokenizer.current_token()

                if token[1] == '(':
                    if default_call:
                        arg_count = 1
                        self.vm_writer.write_push('pointer', 0)
                    self.tokenizer.advance()
                    arg_count += self.compile_expression_list(jack_subroutine)
                    self.vm_writer.write_call(func_class, func_name, arg_count)
                    self.tokenizer.advance()
                elif token_var:
                    self.vm_writer.write_push_symbol(token_var)

    def compile_expression_list(self, jack_subroutine):
        """Compiles a (possibly empty) comma-separated list of expressions"""
        count = 0
        token = self.tokenizer.current_token()

        while token != ('symbol', ')'):
            if token == ('symbol', ','):
                self.tokenizer.advance()

            count += 1
            self.compile_expression(jack_subroutine)
            token = self.tokenizer.current_token()

        return count
    
    @classmethod
    def get_label(cls):
        """Returns the label number"""
        label = 'L{}'.format(cls.num_labels)
        cls.num_labels += 1
        return label
