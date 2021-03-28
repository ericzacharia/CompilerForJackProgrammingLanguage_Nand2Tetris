class VMWriter:
    def __init__(self, output_file):
        self.output_file = output_file
        self.segment_dict = {'static': 'static', 'arg': 'argument', 'var': 'local', 'field': 'this'}

    # Start of Memory Access Commands
    def write_pop_symbol(self, jack_symbol):
        segment_key = jack_symbol[0]
        offset = jack_symbol[2]
        segment_val = self.segment_dict[segment_key]
        self.write_pop(segment_val, offset)

    def write_push_symbol(self, jack_symbol):
        segment_key = jack_symbol[0]
        offset = jack_symbol[2]
        segment_val = self.segment_dict[segment_key]
        self.write_push(segment_val, offset)

    def write_pop(self, segment_val, offset):
        self.output_file.write('pop {0} {1}\n'.format(segment_val, offset))

    def write_push(self, segment_val, offset):
        self.output_file.write('push {0} {1}\n'.format(segment_val, offset))
    # End of Memory Access Commands
    
    # Start of Program Flow Commands
    def write_label(self, label):
        self.output_file.write('label {}\n'.format(label))
        
    def write_goto(self, label):
        self.output_file.write('goto {}\n'.format(label))
        
    def write_if_goto(self, label):
        self.output_file.write('not\n')
        self.output_file.write('if-goto {}\n'.format(label))
    # End of Program Flow Commands
    
    # Start of Subroutine Commands
    def write_function(self, jack_subroutine):
        class_name = jack_subroutine.jack_class.name
        name = jack_subroutine.name
        local_vars = jack_subroutine.var_symbols
        self.output_file.write('function {}.{} {}\n'.format(class_name, name, local_vars))

    def write_call(self, class_name, func_name, arg_count):
        self.output_file.write('call {0}.{1} {2}\n'.format(class_name, func_name, arg_count))
        
    def write_return(self):
        self.output_file.write('return\n')
    # End of Subroutine Commands

    def write_constant(self, n):
        self.write_push('constant', n)

    def write_string(self, string):
        string = string[1:-1]
        self.write_constant(len(string))
        self.write_call('String', 'new', 1)
        for char in string:
            self.write_constant(ord(char))
            self.write_call('String', 'appendChar', 2)

    def write(self, action):
        self.output_file.write('{}\n'.format(action))
