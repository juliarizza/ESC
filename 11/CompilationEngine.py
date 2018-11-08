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
        self.label_counter = 0
        
        self._compile()

    def _compile(self):
        """
            Compiles the whole Jack program.
        """
        # Pula a primeira linha, que identifica o arquivo de tokens
        # Percorre o arquivo até o fim
        self.current_line = self.input.readline()
        while "</tokens>" not in self.current_line:
            self.compileClass()

    def _identify_key(self, line):
        tag_end = line.find('>')
        return line[1:tag_end]

    def _identify_value(self, line):
        first_tag_end = line.find('> ')
        last_tag_start = line.find(' </')
        return line[first_tag_end+2:last_tag_start]

    def _skipLine(self):
        self.current_line = self.input.readline()

    def _generateLabel(self):
        label = "L{}".format(self.label_counter)
        self.label_counter += 1
        return label

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
        while self._identify_value(self.current_line) in ["var", "static", "field"]:
            # Grava e avança a declaração do dado
            kind = self._identify_value(self.current_line)
            self._skipLine()
            # Grava e avança o tipo de dado
            type = self._identify_value(self.current_line)
            self._skipLine()

            # Escreve a declaração até que encontre o último caracter
            while self._identify_value(self.current_line) != ';':
                if self._identify_key(self.current_line) != "symbol":
                    # Se não for uma vírgula, é um novo nome de variável
                    # Grava e avança o nome
                    name = self._identify_value(self.current_line)
                    self._skipLine()
                    # Adiciona a variável à symbol table
                    self.symbol_table.define(name, type, kind)
                else:
                    # Se for uma vírgula, avança a linha
                    self._skipLine()

            # Avança o último caracter ;
            self._skipLine()

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
                self._skipLine()
                # Adiciona o argumento à symbol table da subrotina
                self.symbol_table.define(name, type, "argument")
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
        while self._identify_value(self.current_line) == "var":
            # Grava e avança a declaração da variável <keyword> var </keyword>
            kind = self._identify_value(self.current_line)
            self._skipLine()
            # Grava e avança o tipo da variável <keyword> int </keyword>
            type = self._identify_value(self.current_line)
            self._skipLine()

            # Avança a declaração até que encontre o último caracter
            while self._identify_value(self.current_line) != ';':
                if self._identify_key(self.current_line) != "symbol":
                    # Se não for uma vírgula, é um novo nome de variável
                    # Grava e avança o nome da variável
                    name = self._identify_value(self.current_line)
                    self._skipLine()
                    # Adiciona a variável à symbol table
                    self.symbol_table.define(name, type, kind)
                else:
                    # Avança a vírgula
                    self._skipLine()

            # Avança o último caracter ;
            self._skipLine()

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
        # Avança a keyword <keyword> let </keyword>
        self._skipLine()
        # Grava e avança o nome da variável <identifier> nome </identifier>
        name = self._identify_value(self.current_line)
        self._skipLine()

        # Se tiver [, é de um array e deve conter uma expressão dentro
        if self._identify_value(self.current_line) == '[':
            # Avança a abertura de chave [
            self._skipLine()
            # Compila a expressão
            self.compileExpression()
            # Avança o fechamento de chave ]
            self._skipLine()

        # Avança a associação <symbol> = </symbol>
        self._skipLine()
        # Compila a expressão
        self.compileExpression()
        # Avança o fim da declaração <symbol> ; </symbol>
        self._skipLine()

        # Escreve o resultado da expressão na variável usando o pop
        kind = self.symbol_table.kindOf(name)
        index = self.symbol_table.indexOf(name)
        self.code_writer.writePop(kind, index)

    def compileIf(self):
        """
            Compiles an if statement,
            possibly with a trailing else clause.
        """
        else_label = self._generateLabel()
        end_label = self._generateLabel()

        # Avança a keyword <keyword> if </keyword>
        self._skipLine()
        # Avança o início da expressão <symbol> ( </symbol>
        self._skipLine()
        # Compila a expressão de verificação
        self.compileExpression()
        # Avança o fim da expressão <symbol> ) </symbol>
        self._skipLine()

        # Nega a expressão de verificação no arquivo .vm
        self.code_writer.writeArithmetic("~")
        # Redireciona para o else no arquivo .vm
        self.code_writer.writeIf(else_label)

        # Inicia o bloco do if <symbol> { </symbol>
        self._skipLine()
        while self._identify_value(self.current_line) != '}':
            self.compileStatements()
        # Avança o fim do bloco <symbol> } </symbol>
        self._skipLine()

        # Redireciona para o fim da verificação no .vm
        self.code_writer.writeGoto(end_label)
        # Escreve a label do else no arquivo .vm
        self.code_writer.writeLabel(else_label)

        # Confere se existe um bloco else
        if self._identify_value(self.current_line) == "else":
            # Avança o else <keyword> else </keyword>
            self._skipLine()
            # Avança o início do bloco <symbol> { </symbol>
            self._skipLine()
            # Escreve o conteúdo do bloco
            while self._identify_value(self.current_line) != '}':
                self.compileStatements()
            # Avança o fim do bloco <symbol> } </symbol>
            self._skipLine()

        # Escreve a label de fim de bloco
        self.code_writer.writeLabel(end_label)

    def compileWhile(self):
        """
            Compiles a while statement.
        """
        # Define as 2 labels necessárias
        start_label = self._generateLabel()
        end_label = self._generateLabel()

        # Escreve a label de início no arquivo .vm
        self.code_writer.writeLabel(start_label)

        # Avança o início da declaração <keyword> while </keyword>
        self._skipLine()
        # Avança o início da expressão <symbol> ( </symbol>
        self._skipLine()
        # Compila a expressão de verificação
        self.compileExpression()

        # Nega a expressão de verificação no arquivo .vm
        self.code_writer.writeArithmetic("~")
        # Verifica a expressão e escreve um if-goto no arquivo .vm
        self.code_writer.writeIf(end_label)

        # Avança o fim da expressão </symbol> ) </symbol>
        self._skipLine()
        # Avança o início do bloco e continua até o fim do mesmo
        self._skipLine()
        # Compila o conteúdo do while
        while self._identify_value(self.current_line) != '}':
            self.compileStatements()
        # Avança o fim do bloco <symbol> } </symbol>
        self._skipLine()

        # Escreve um goto no arquivo para voltar ao início do loop no .vm
        self.code_writer.writeGoto(start_label)
        # Escreve label final para sair do loop no .vm
        self.code_writer.writeLabel(end_label)


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
            name = self._identify_value(self.current_line)
            self._skipLine()

            if self._identify_value(self.current_line) == '.':
                # Se a linha for um símbolo . é uma chamada a uma função
                # Grava e avança o ponto
                name += "."
                self._skipLine()
                # Grava e avança o nome da função
                name += self._identify_value(self.current_line)
                self._skipLine()
                # Avança o símbolo de início da chamada (
                self._skipLine()
                # Se houver uma expressão dentro da chamada, compila
                # Se não, compila a lista em branco
                n_args = self.compileExpressionList()
                # Avança o símbolo de fim da chamada )
                self._skipLine()
                # Escreve a chamada da função no arquivo .vm
                self.code_writer.writeCall(name, n_args)
            elif self._identify_value(self.current_line) == '[':
                # Se a linha for um símbolo [ é um acesso ao array
                # Avança a chave [
                self._skipLine()
                # Compila a expressão dentro das chaves
                self.compileExpression()
                # Avança a chave ]
                self._skipLine()

                kind = self.symbol_table.kindOf(name)
                index = self.symbol_table.indexOf(name)
                # Escreve o push do array no arquivo .vm
                self.code_writer.writePush(kind, index)

                self.code_writer.writeArithmetic('+')
                self.code_writer.writePop('pointer', 1)
                self.code_writer.writePush('that', 0)
            else:
                # Faz o push do identifier no arquivo .vm
                kind = self.symbol_table.kindOf(name)
                index = self.symbol_table.indexOf(name)
                self.code_writer.writePush(kind, index)
        elif self._identify_value(self.current_line) == '(':
            # Avança a abertura de expressão (
            self._skipLine()
            # Compila a expressão
            self.compileExpression()
            # Avança o encerramento da expressão )
            self._skipLine()
        elif self._identify_key(self.current_line) == "keyword":
            # Faz o push do valor no arquivo .vm
            value = self._identify_value(self.current_line)
            if value == "true":
                self.code_writer.writePush("constant", 0)
                self.code_writer.writeArithmetic('~')
            elif value == "false":
                self.code_writer.writePush("constant", 0)
            self._skipLine()
        elif self._identify_key(self.current_line) == "stringConstant":
            # Grava a string
            string = self._identify_value(self.current_line)

            # Escreve o tamanho e chama a criação de string no arquivo .vm
            self.code_writer.writePush("constant", len(string))
            self.code_writer.writeCall("String.appendChar", 1)

            # Escreve o código e adiciona cada caracter no arquivo .vm
            for char in string:
                self.code_writer.writePush("constant", ord(char))
                self.code_writer.writeCall("String.appendChar", 2)
        elif self._identify_key(self.current_line) == "integerConstant":
            # Adiciona a constante à pilha
            num = self._identify_value(self.current_line)
            self.code_writer.writePush("constant", num)
            # Avança a linha
            self._skipLine()
        elif self._identify_value(self.current_line) in ['-', '~']:
            # É um operador unário e ainda tem outra parte do termo
            # depois dele, portanto escreve o operador e o próximo termo
            op = self._identify_value(self.current_line)
            op = op if op == '~' else 'neg'
            self._skipLine()
            self.compileTerm()
            self.code_writer.writeArithmetic(op)

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
