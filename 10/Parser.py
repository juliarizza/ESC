import os

class CompilationEngine():
    OPERATORS = ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']

    def __init__(self, token_file, output_file):
        """
            Creates a new compilation engine with
            the given input and output.
            The next routine called must be compileClass.
        """
        if os.path.exists(output_file):
            os.remove(output_file)

        self.input = open(token_file, 'r')
        self.output = open(output_file, 'a+')
        self.current_line = self.input.readline()
        self.indent = 0


        self._compile()

    def _compile(self):
        """
            Compiles the whole Jack program.
        """
        # Pula a primeira linha, que identifica o arquivo de tokens
        # Percorre o arquivo até o fim
        self.current_line = self.input.readline()
        while "</tokens>" not in self.current_line:
            keyword = self._identify_value(self.current_line)

            if keyword == "class":
                self.compileClass()
            elif keyword == "function":
                self.compileSubroutineDec()
            elif keyword == "var":
                self.varDec()
            elif keyword in ["let", "if", "while", "do", "return"]:
                self.compileStatements()
            else:
                print("----- Não foi possível identificar a linha atual.")
                self.current_line = self.input.readline()

    def _identify_key(self, line):
        tag_end = line.find('>')
        return line[1:tag_end]

    def _identify_value(self, line):
        first_tag_end = line.find('> ')
        last_tag_start = line.find(' <')
        return line[first_tag_end+2:last_tag_start]

    def _writeLine(self):
        """
            Writes the current line to the output file.
        """
        # Substitui os caracteres especiais pelos caracteres seguros
        symbol = self.current_line.replace("<symbol> ", '')
        symbol = symbol.replace(" </symbol>", '')
        symbol = symbol.replace('\n', '')

        self.output.write("{0}{1}".format(
            " " * 2 * self.indent,
            self.current_line
        ))

        self.current_line = self.input.readline()

    def compileClass(self):
        """
            Compiles a complete class.
        """
        self.output.write("<class>\n")
        self.indent += 1

        # Escreve <keyword> class </keyword>
        self._writeLine()
        # Escreve o nome da classe <identifier> nome </identifier>
        self._writeLine()
        # Escreve o símbolo de início da classe <symbol> { </symbol>
        self._writeLine()

        self.compileClassVarDec()
        self.compileSubroutineDec()

        # Escreve o símbolo de fechamento da classe <symbol> } </symbol>
        self._writeLine()

        self.indent -= 1
        self.output.write("</class>\n")

    def compileClassVarDec(self):
        """
            Compiles a static variable declaration,
            or a field declaration.
        """
        # Escreve múltiplas declarações de variável seguidas
        while "var" in self.current_line or "static" in self.current_line \
            or "field" in self.current_line:
            self.output.write("{}<classVarDec>\n".format(" " * 2 * self.indent))
            self.indent += 1

            # Escreve a declaração até que encontre o último caracter
            while ';' not in self.current_line:
                self._writeLine()

            # Escreve o último caracter
            self._writeLine()

            self.indent -= 1
            self.output.write("{}</classVarDec>\n".format(" " * 2 * self.indent))

    def compileSubroutineDec(self):
        """
            Compiles a complete method, function,
            or constructor.
        """
        # Escrever múltiplos métodos ou funções seguidos
        while "method" in self.current_line or "function" in self.current_line \
            or "constructor" in self.current_line:
            self.output.write("{}<subroutineDec>\n".format(" " * 2 * self.indent))
            self.indent += 1

            # Escreve a declaração <keyword> function </keyword>
            self._writeLine()
            # Escreve o tipo de retorno <keyword> void </keyword>
            self._writeLine()
            # Escreve o nome da função <identifier> nome </identifier>
            self._writeLine()
            # Escreve a declaração dos parâmetros <symbol> ( </symbol>
            self._writeLine()
            # Escreve a lista de parâmetros
            self.compileParameterList()
            # Escreve a conclusão dos parâmetros <symbol> ) </symbol>
            self._writeLine()

            self.compileSubroutineBody()

            self.indent -= 1
            self.output.write("{}</subroutineDec>\n".format(" " * 2 * self.indent))

    def compileParameterList(self):
        """
            Compiles a (possibly empty) parameter
            list. Does not handle the enclosin "()".
        """
        self.output.write("{}<parameterList>\n".format(" " * 2 * self.indent))
        self.indent += 1

        # Escreve todas as linhas até encontrar o caracter de fim de parâmetros
        while ')' not in self.current_line:
            self._writeLine()

        self.indent -= 1
        self.output.write("{}</parameterList>\n".format(" " * 2 * self.indent))

    def compileSubroutineBody(self):
        """
            Compiles a subroutine's body.
        """
        self.output.write("{}<subroutineBody>\n".format(" " * 2 * self.indent))
        self.indent += 1

        # Escreve a abertura de bloco <symbol> { </symbol>
        self._writeLine()

        self.compileVarDec()
        self.compileStatements()

        # Escreve o término do bloco <symbol> } </symbol>
        self._writeLine()

        self.indent -= 1
        self.output.write("{}</subroutineBody>\n".format(" " * 2 * self.indent))

    def compileVarDec(self):
        """
            Compiles a var declaration.
        """
        # Escreve múltiplas declarações de variáveis seguidas
        while "var" in self.current_line:
            self.output.write("{}<varDec>\n".format(" " * 2 * self.indent))
            self.indent += 1

            # Escreve a declaração até que encontre o último caracter
            while ' ; ' not in self.current_line:
                self._writeLine()

            # Escreve o último caracter
            self._writeLine()

            self.indent -= 1
            self.output.write("{}</varDec>\n".format(" " * 2 * self.indent))

    def compileStatements(self):
        """
            Compiles a sequence os statements.
            Does not handle the enclosing "{}";
        """
        self.output.write("{}<statements>\n".format(" " * 2 * self.indent))
        self.indent += 1

        keyword = self._identify_value(self.current_line)

        # Escreve múltiplos statements
        while keyword in ["let", "if", "while", "do", "return"]:
            if keyword == "let":
                self.compileLet()
            elif keyword == "if":
                self.compileIf()
            elif keyword == "while":
                self.compileWhile()
            elif keyword == "do":
                self.compileDo()
            elif keyword == "return":
                self.compileReturn()

            keyword = self._identify_value(self.current_line)

        self.indent -= 1
        self.output.write("{}</statements>\n".format(" " * 2 * self.indent))

    def compileLet(self):
        """
            Compiles a let statement.
        """
        self.output.write("{}<letStatement>\n".format(" " * 2 * self.indent))
        self.indent += 1

        # Escreve a keyword <keyword> let </keyword>
        self._writeLine()
        # Escreve o nome da variável <identifier> nome </identifier>
        self._writeLine()

        # Se tiver [, é de um array e deve conter uma expressão dentro
        if self._identify_value(self.current_line) == '[':
            # Escreve a abertura de chave [
            self._writeLine()
            # Escreve a expressão
            self.compileExpression()
            # Escreve o fechamento de chave ]
            self._writeLine()

        # Escreve a associação <symbol> = </symbol>
        self._writeLine()
        # Escreve a expressão
        self.compileExpression()
        # Escreve o fim da declaração <symbol> ; </symbol>
        self._writeLine()

        self.indent -= 1
        self.output.write("{}</letStatement>\n".format(" " * 2 * self.indent))

    def compileIf(self):
        """
            Compiles an if statement,
            possibly with a trailing else clause.
        """
        self.output.write("{}<ifStatement>\n".format(" " * 2 * self.indent))
        self.indent += 1

        # Escreve a keyword <keyword> if </keyword>
        self._writeLine()
        # Escreve o início da expressão <symbol> ( </symbol>
        self._writeLine()
        # Escreve a expressão
        self.compileExpression()
        # Escreve o fim da expressão <symbol> ) </symbol>
        self._writeLine()
        # Escreve o início do bloco e continua até o fim do mesmo
        self._writeLine()
        while '}' not in self.current_line:
            self.compileStatements()
        # Escreve o fim do bloco <symbol> } </symbol>
        self._writeLine()

        # Confere se existe um bloco else
        if 'else' in self.current_line:
            # Escreve o else <keyword> else </keyword>
            self._writeLine()
            # Escreve o início do bloco <symbol> { </symbol>
            self._writeLine()
            # Escreve o conteúdo do bloco
            while '}' not in self.current_line:
                self.compileStatements()
            # Escreve o fim do bloco <symbol> } </symbol>
            self._writeLine()

        self.indent -= 1
        self.output.write("{}</ifStatement>\n".format(" " * 2 * self.indent))

    def compileWhile(self):
        """
            Compiles a while statement.
        """
        self.output.write("{}<whileStatement>\n".format(" " * 2 * self.indent))
        self.indent += 1

        # Escreve o início da declaração <keyword> while </keyword>
        self._writeLine()
        # Escreve o início da expressão <symbol> ( </symbol>
        self._writeLine()
        # Escreve a expressão
        self.compileExpression()
        # Escreve o fim da expressão </symbol> ) </symbol>
        self._writeLine()
        # Escreve o início do bloco e continua até o fim do mesmo
        self._writeLine()
        while '}' not in self.current_line:
            self.compileStatements()
        # Escreve o fim do bloco <symbol> } </symbol>
        self._writeLine()

        self.indent -= 1
        self.output.write("{}</whileStatement>\n".format(" " * 2 * self.indent))

    def compileDo(self):
        """
            Compiles a do statement.
        """
        self.output.write("{}<doStatement>\n".format(" " * 2 * self.indent))
        self.indent += 1

        # Escreve todos os elementos até iniciar a lista de expressões
        while '(' not in self.current_line:
            self._writeLine()
        # Escreve o início da lista <symbol> ( </symbol>
        self._writeLine()
        # Escreve a lista
        self.compileExpressionList()
        # Escreve o fim da lista <symbol> ) </symbol>
        self._writeLine()
        # Escreve o fim do statement <symbol> ; </symbol>
        self._writeLine()

        self.indent -= 1
        self.output.write("{}</doStatement>\n".format(" " * 2 * self.indent))

    def compileReturn(self):
        """
            Compiles a return statement.
        """
        self.output.write("{}<returnStatement>\n".format(" " * 2 * self.indent))
        self.indent += 1

        # Escreve o ínicio da declaração <keyword> return </keyword>
        self._writeLine()
        # Escreve a expressão
        if not "symbol" in self.current_line:
            self.compileExpression()
        # Escreve o fim da declaração <symbol> ; </symbol>
        self._writeLine()

        self.indent -= 1
        self.output.write("{}</returnStatement>\n".format(" " * 2 * self.indent))

    def compileExpression(self):
        """
            Compiles an expression.
        """
        self.output.write("{}<expression>\n".format(" " * 2 * self.indent))
        self.indent += 1

        # Sempre inicia com um termo
        self.compileTerm()

        # Verificamos a necessidade de outro termo
        if self._identify_value(self.current_line) in self.OPERATORS:
            # Escreve o operador
            self._writeLine()
            # Escreve o próximo termo
            self.compileTerm()

        self.indent -= 1
        self.output.write("{}</expression>\n".format(" " * 2 * self.indent))

    def compileTerm(self):
        """
            Compiles a term. If the current token
            is an identifier, the routine must
            distinguish between a variable , an
            array entry, or a subroutine call. A
            single look-ahead token, which may be one of
            "[", "(", or ".", suffices to distinguish
            between the possibilities. Any other token is
            not part of this term and should not be advanced
            over.
        """
        self.output.write("{}<term>\n".format(" " * 2 * self.indent))
        self.indent += 1

        if "identifier" in self.current_line:
            # Pode ser um nome de variável ou uma chamada de função
            # var[expressao], funcao.chamada()
            # Por isso escrevemos o identificador e
            # verificamos por caracteres especiais
            self._writeLine()

            if '.' in self.current_line:
                # Se a linha for um símbolo . é uma chamada a uma função
                # Escreve o ponto
                self._writeLine()
                #Escreve o nome da função
                self._writeLine()
                # Escreve o símbolo de início da chamada (
                self._writeLine()
                # Se houver uma expressão dentro da chamada, escreve
                # Se não, escreve a lista em branco
                self.compileExpressionList()
                # Escreve o símbolo de fim da chamada )
                self._writeLine()
            elif '[' in self.current_line:
                # Se a linha for um símbolo [ é um acesso ao array
                # Escreve a chave [
                self._writeLine()
                # Escreve a expressão dentro das chaves
                self.compileExpression()
                # Escreve a chave ]
                self._writeLine()
        elif self._identify_value(self.current_line) == '(':
            # Escreve a abertura de expressão (
            self._writeLine()
            # Escreve a expressão
            self.compileExpression()
            # Escreve o encerramento da expressão )
            self._writeLine()
        elif "keyword" in self.current_line:
            self._writeLine()
        elif "stringConstant" in self.current_line:
            self._writeLine()
        elif "integerConstant" in self.current_line:
            self._writeLine()
        elif self._identify_value(self.current_line) in ['-', '~']:
            # É um operador unário e ainda tem outra parte do termo
            # depois dele, portanto escreve o operador e o próximo termo
            self._writeLine()
            self.compileTerm()


        self.indent -= 1
        self.output.write("{}</term>\n".format(" " * 2 * self.indent))

    def compileExpressionList(self):
        """
            Compiles a (possibly empty) comma-separated
            list of expressions.
        """
        self.output.write("{}<expressionList>\n".format(" " * 2 * self.indent))
        self.indent += 1

        while ')' not in self.current_line:
            if ',' in self.current_line:
                self._writeLine()
            else:
                self.compileExpression()

        self.indent -= 1
        self.output.write("{}</expressionList>\n".format(" " * 2 * self.indent))
