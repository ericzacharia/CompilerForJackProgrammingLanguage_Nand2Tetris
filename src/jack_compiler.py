from jack_tokenizer import JackTokenizer
from compilation_engine import CompilationEngine
import sys
import os


def compile_file(file_path):
    with open(file_path, 'r') as rf:
        file_path_no_ext, jack_extension = os.path.splitext(file_path)
        output_path = file_path_no_ext + '.vm'
        with open(output_path, 'w') as wf:
            tokenizer = JackTokenizer(rf.read())
            compiler = CompilationEngine(tokenizer, wf)
            compiler.compile_class()


def compile_dir(dir_path):
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        file_path_no_ext, extension = os.path.splitext(file_path)
        if os.path.isfile(file_path) and extension == '.jack':
            compile_file(file_path)


arg = sys.argv[1]
if os.path.isdir(arg):
    compile_dir(arg)
else:
    compile_file(arg)
