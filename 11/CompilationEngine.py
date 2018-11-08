import os
from SymbolTable import SymbolTable
from VMWriter import VMWriter

"""
    - Gets its input from a JackTockenizer and writes its output
    using the VMWriter.
    - Organized as a series of compilexxx routines, xxx being a
    syntatic element in the Jack language.
"""

class CompilationEngine():
    OPERATORS = ['+', '-', '*', '/', '&', '|', '<', '>', '=']

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
        self.symbol_table = None
        self.code_writer = VMWriter(output_file)
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
                self.compileVarDec()
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
        last_tag_start = line.find(' </')
        return line[first_tag_end+2:last_tag_start]

    def _writeLine(self, line=None):
        """
            Writes the current line to the output file.
        """
        if not line:
            self.output.write("{0}{1}".format(
                " " * 2 * self.indent,
                self.current_line
            ))
            self.current_line = self.input.readline()
        else:
            self.output.write("{0}{1}".format(
                " " * 2 * self.indent,
                line
            ))
            self.current_line = self.input.readline()

    def _skipLine(self):
        self.current_line = self.input.readline()

    def compileClass(self):
        """
            Compiles a complete class.
        """
        # Cada classe nova deve ter uma symbol table nova
        self.symbol_table = SymbolTable()

        # Avança a linha <keyword> class </keyword>
        self._skipLine()
        # Grava e avança o nome da classe <identifier> nome </identifier>
        name = self._identify_value(self.current_line)
        self._skipLine()
        # Avança o símbolo de início da classe <symbol> { </symbol>
        self._skipLine()

        self.compileClassVarDec()
        self.compileSubroutineDec(name)

        # Avança o símbolo de fechamento da classe <symbol> } </symbol>
        self._skipLine()

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

            # Identifica a declaração do dado
            type = self._identify_value(self.current_line)
            # Escreve a declaração do dado
            self.current_line = self.input.readline()
            # Identifica o tipo do dado
            kind = self._identify_value(self.current_line)
            # Escreve o tipo do dado
            self.current_line = self.input.readline()

            # Escreve a declaração até que encontre o último caracter
            while ' ; ' not in self.current_line:
                if not "symbol" in self.current_line:
                    # Se não for uma vírgula, é um novo nome de variável
                    name = self._identify_value(self.current_line)
                    # Adiciona a variável à symbol table
                    self.symbol_table.define(name, type, kind)
                    index = self.symbol_table.indexOf(name)
                    # Escreve o nome da variável
                    self._writeLine(f"<{kind}> {index} </{kind}>\n")
                else:
                    self._writeLine()

            # Escreve o último caracter ;
            self._writeLine()

            self.indent -= 1
            self.output.write("{}</classVarDec>\n".format(" " * 2 * self.indent))

    def compileSubroutineDec(self, class_name):
        """
            Compiles a complete method, function,
            or constructor.
        """
        # Analisa múltiplos métodos ou funções seguidos
        while self._identify_value(self.current_line) in [
                "method", "function", "constructor"
            ]:
            # Cria uma nova symbol table para o escopo da subrotina
            self.symbol_table.startSubroutine()

            # Avança a declaração <keyword> function </keyword>
            self._skipLine()
            # Grava e avança o tipo de retorno <keyword> void </keyword>
            type = self._identify_value(self.current_line)
            self._skipLine()
            # Grava e avança o nome da função <identifier> nome </identifier>
            name = self._identify_value(self.current_line)
            self._skipLine()
            # Avança a declaração dos parâmetros <symbol> ( </symbol>
            self._skipLine()
            # Recebe e grava a quantidade de parâmetros na lista de parâmetros
            n_params = self.compileParameterList()
            # Avança a conclusão dos parâmetros <symbol> ) </symbol>
            self._skipLine()

            # Escreve a declaração da função no arquivo .vm
            self.code_writer.writeFunction(
                "{}.{}".format(class_name, name),
                n_params
            )

            self.compileSubroutineBody()

    def compileParameterList(self):
        """
            Compiles a (possibly empty) parameter
            list. Does not handle the enclosin "()".
        """
        parameters_count = 0

        # Escreve todas as linhas até encontrar o caracter de fim de parâmetros
        while self._identify_value(self.current_line) != ')':
            if self._identify_key(self.current_line) != "symbol":
                # Guarda e avança o tipo do argumento <keyword> int </keyword>
                type = self._identify_value(self.current_line)
                self._skipLine()
                # Guarda o nome do argumento <identifier> nome </identifier>
                name = self._identify_value(self.current_line)
                # Adiciona o argumento à symbol table da subrotina
                self.symbol_table.define(name, type, "argument")
                # Escreve o código para o push no .vm
                index = self.symbol_table.indexOf(name)
                self.code_writer.writePush("argument", index)
                # Aumenta a contagem de parâmetros
                parameters_count += 1
            else:
                # Avança a vírgula
                self._skipLine()

        return parameters_count

    def compileSubroutineBody(self):
        """
            Compiles a subroutine's body.
        """
        # Avança a abertura de bloco <symbol> { </symbol>
        self._skipLine()

        self.compileVarDec()
        self.compileStatements()

        # Avança o término do bloco <symbol> } </symbol>
        self._skipLine()

    def compileVarDec(self):
        """
            Compiles a var declaration.
        """
        # Escreve múltiplas declarações de variáveis seguidas
        while "var" in self.current_line:
            self.output.write("{}<varDec>\n".format(" " * 2 * self.indent))
            self.indent += 1

            # Escreve a declaração da variável
            kind = self._identify_value(self.current_line)
            self.current_line = self.input.readline()
            # Escreve o tipo da variável
            type = self._identify_value(self.current_line)
            self.current_line = self.input.readline()

            # Escreve a declaração até que encontre o último caracter
            while ' ; ' not in self.current_line:
                if not "symbol" in self.current_line:
                    # Se não for uma vírgula, é um novo nome de variável
                    name = self._identify_value(self.current_line)
                    # Adiciona a variável à symbol table
                    self.symbol_table.define(name, type, kind)
                    index = self.symbol_table.indexOf(name)
                    # Escreve o nome da variável
                    self._writeLine(f"<{kind}> {index} </{kind}>\n")
                else:
                    self._writeLine()

            # Escreve o último caracter ;
            self._writeLine()

            self.indent -= 1
            self.output.write("{}</varDec>\n".format(" " * 2 * self.indent))

    def compileStatements(self):
        """
            Compiles a sequence os statements.
            Does not handle the enclosing "{}";
        """
        keyword = self._identify_value(self.current_line)

        # Verifica múltiplos statements
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
        # Avança o comando <keyword> do </keyword>
        self._skipLine()
        # Identifica a função a ser chamada até o início dos parâmetros
        function = ""
        while self._identify_value(self.current_line) != '(':
            # Adiciona o valor para montar o nome da chamda
            function += self._identify_value(self.current_line)
            # Avança para o próximo valor
            self._skipLine()

        # Avança o início da lista de expressões <symbol> ( </symbol>
        self._skipLine()
        # Compila a lista de expressões
        n_args = self.compileExpressionList()
        # Avança o fim da lista <symbol> ) </symbol>
        self._skipLine()
        # Avança o fim do statement <symbol> ; </symbol>
        self._skipLine()

        # Escreve a chamada da função no arquivo .vm
        self.code_writer.writeCall(function, n_args)

        # Como a função 'do' não retorna nada, precisamos fazer um pop
        # do valor gerado para a pilha temporária
        self.code_writer.writePop("temp", 0)

    def compileReturn(self):
        """
            Compiles a return statement.
        """
        # Avança o ínicio da declaração <keyword> return </keyword>
        self._skipLine()
        if self._identify_key(self.current_line) != "symbol":
            # Compila a expressão de retorno
            self.compileExpression()
        else:
            # A função não retorna nada, mas é esperado um valor de retorno
            # Por isso informamos 0
            self.code_writer.writePush("constant", 0)
        # Avança o fim da declaração <symbol> ; </symbol>
        self._skipLine()

        # Escreve o comando de return no arquivo .vm
        self.code_writer.writeReturn()

    def compileExpression(self):
        """
            Compiles an expression.
        """
        # Sempre inicia com um termo
        self.compileTerm()

        # Verificamos a necessidade de outro termo
        operator = self._identify_value(self.current_line)
        if operator in self.OPERATORS:
            # Avança o operador
            self._skipLine()
            # Compila o próximo termo
            self.compileTerm()
            # Escreve a operação no arquivo
            self.code_writer.writeArithmetic(operator)

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
        if self._identify_key(self.current_line) == "identifier":
            # Pode ser um nome de variável ou uma chamada de função
            # var[expressao], funcao.chamada()
            # Por isso gravamos e avançamos o identificador e
            # verificamos por caracteres especiais
            nome = self._identify_value(self.current_line)
            self._skipLine()

            if self._identify_value(self.current_line) == '.':
                # Se a linha for um símbolo . é uma chamada a uma função
                # Grava e avança o ponto
                nome += "."
                self._writeLine()
                # Grava e avança o nome da função
                nome += self._identify_value(self.current_line)
                self._writeLine()
                # Avança o símbolo de início da chamada (
                self._writeLine()
                # Se houver uma expressão dentro da chamada, compila
                # Se não, compila a lista em branco
                n_args = self.compileExpressionList()
                # Avança o símbolo de fim da chamada )
                self._writeLine()
            elif self._identify_value(self.current_line) == '[':
                # Se a linha for um símbolo [ é um acesso ao array
                # Avança a chave [
                self._writeLine()
                # Compila a expressão dentro das chaves
                self.compileExpression()
                # Avança a chave ]
                self._writeLine()
        elif self._identify_value(self.current_line) == '(':
            # Avança a abertura de expressão (
            self._skipLine()
            # Compila a expressão
            self.compileExpression()
            # Avança o encerramento da expressão )
            self._skipLine()
        elif "keyword" in self.current_line:
            self._writeLine()
        elif "stringConstant" in self.current_line:
            self._writeLine()
        elif self._identify_key(self.current_line) == "integerConstant":
            # Adiciona a constante à pilha
            num = self._identify_value(self.current_line)
            self.code_writer.writePush("constant", num)
            # Avança a linha
            self._skipLine()
        elif self._identify_value(self.current_line) in ['-', '~']:
            # É um operador unário e ainda tem outra parte do termo
            # depois dele, portanto escreve o operador e o próximo termo
            self._writeLine()
            self.compileTerm()

    def compileExpressionList(self):
        """
            Compiles a (possibly empty) comma-separated
            list of expressions.
        """
        arguments_count = 0

        while self._identify_value(self.current_line) != ')':
            if self._identify_value(self.current_line) == ',':
                # Avança a vírgula
                self._skipLine()
            else:
                # Compila a expressão
                self.compileExpression()
                # Incrementa a contagem de argumentos
                arguments_count += 1

        return arguments_count
