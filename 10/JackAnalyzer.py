import os
import sys
from JackTokenizer import JackTokenizer
from Parser import CompilationEngine

def compile_from_file(file):
    filename_w_ext = os.path.basename(file)
    filename, extension = os.path.splitext(filename_w_ext)

    output_token = os.path.join(os.path.dirname(file), "{}T.xml".format(filename))
    output_xml = os.path.join(os.path.dirname(file), "{}.xml".format(filename))


    tokenizer = JackTokenizer(file, output_token)
    ce = CompilationEngine(output_token, output_xml)

if __name__ == "__main__":
    partial_path = sys.argv[1]

    absolut_path = os.path.abspath(partial_path)
    if os.path.isdir(absolut_path):
        for file in os.listdir(absolut_path):
            if file.endswith(".jack"):
                jack_file = os.path.join(absolut_path, file)
                compile_from_file(jack_file)
    else:
        compile_from_file(absolut_path)
