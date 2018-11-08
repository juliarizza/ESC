class VMWriter():
    def __init__(self, output_file):
        """
            Creates a new output .vm file
            and prepares it for writing.
        """
        this.output = open(output_file, 'a+')

    def writePush(self, segment, index):
        """
            Writes a VM push command.
        """
        this.output.write("push {} {}\n".format(segment, index))

    def writePop(self, segment, index):
        """
            Writes a VM pop command.
        """
        this.output.write("pop {} {}\n".format(segment, index))

    def writeArithmetic(self, command):
        """
            Writes a VM arithmetic-logical
            command.
        """
        this.output.write("{}\n".format(command))

    def writeLabel(self, label):
        """
            Writes a VM label command.
        """
        this.output.write("label {}\n".format(label))

    def writeGoto(self, label):
        """
            Writes a VM goto command.
        """
        this.output.write("goto {}\n".format(label))

    def writeIf(self, label):
        """
            Writes a VM if command.
        """
        this.output.write("if-goto {}\n".format(label))

    def writeCall(self, name, nArgs):
        """
            Writes a VM call command.
        """
        this.output.write("call {} {}\n".format(name, nArgs))

    def writeFunction(self, name, nLocals):
        """
            Writes a VM function command.
        """
        this.output.write("function {} {}\n".format(name, nLocals))

    def writeReturn(self):
        """
            Writes a VM return command.
        """
        this.output.write("return\n")

    def close(self):
        """
            Closes the output file.
        """
        this.output.close()
