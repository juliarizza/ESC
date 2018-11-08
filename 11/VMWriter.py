class VMWriter():
    ARITHMETIC_COMMANDS = {
        "+" : "add",
        "-" : "sub",
        "~" : "not",
        ">" : "gt",
        "<" : "lt",
        "&" : "and",
        "=" : "eq",
        "neg" : "neg"
    }

    EXTERNAL_ARITHMETICS = {
        "*" : "Math.multiply"
    }

    def __init__(self, output_file):
        """
            Creates a new output .vm file
            and prepares it for writing.
        """
        self.output = open(output_file, 'a+')

    def writePush(self, segment, index):
        """
            Writes a VM push command.
        """
        self.output.write("push {} {}\n".format(segment, index))

    def writePop(self, segment, index):
        """
            Writes a VM pop command.
        """
        self.output.write("pop {} {}\n".format(segment, index))

    def writeArithmetic(self, operator):
        """
            Writes a VM arithmetic-logical
            command.
        """
        if operator in self.ARITHMETIC_COMMANDS.keys():
            self.output.write("{}\n".format(self.ARITHMETIC_COMMANDS[operator]))
        elif operator in self.EXTERNAL_ARITHMETICS.keys():
            self.writeCall(self.EXTERNAL_ARITHMETICS[operator], 2)

    def writeLabel(self, label):
        """
            Writes a VM label command.
        """
        self.output.write("label {}\n".format(label))

    def writeGoto(self, label):
        """
            Writes a VM goto command.
        """
        self.output.write("goto {}\n".format(label))

    def writeIf(self, label):
        """
            Writes a VM if command.
        """
        self.output.write("if-goto {}\n".format(label))

    def writeCall(self, name, nArgs):
        """
            Writes a VM call command.
        """
        self.output.write("call {} {}\n".format(name, nArgs))

    def writeFunction(self, name, nLocals):
        """
            Writes a VM function command.
        """
        self.output.write("function {} {}\n".format(name, nLocals))

    def writeReturn(self):
        """
            Writes a VM return command.
        """
        self.output.write("return\n")

    def close(self):
        """
            Closes the output file.
        """
        self.output.close()
