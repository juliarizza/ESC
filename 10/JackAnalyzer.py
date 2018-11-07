import os
import sys
from JackTokenizer import JackTokenizer
from Parser import CompilationEngine

if __name__ == "__main__":
    partial_path = sys.argv[1]
    filename_w_ext = os.path.basename(partial_path)
    filename, extension = os.path.splitext(filename_w_ext)

    file = os.path.join(os.path.dirname(os.path.realpath(__file__)), partial_path)
    tokens = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"T{filename}.xml")

    tokenizer = JackTokenizer(file, filename)
    ce = CompilationEngine(tokens, filename)
