import os

class JackTokenizer():
    TOKEN_TYPES = {
        "KEYWORD": "keyword",
        "SYMBOL": "symbol",
        "IDENTIFIER": "identifier",
        "INT_CONST": "integerConstant",
        "STRING_CONST": "stringConstant"
    }

    KEYWORDS = [
        "class", "constructor", "function", "method",
        "field", "static", "var", "int", "char", "boolean",
        "void", "true", "false", "null", "this", "let", "do",
        "if", "else", "while", "return"
    ]

    SYMBOLS = [
        '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-',
        '*', '/', '&', '|', '<', '>', '=', '~'
    ]

    def __init__(self, input_file, output_file):
        """
            Opens the input .jack file and gets ready to
            tokenize it.
        """
        if os.path.exists(output_file):
            os.remove(output_file)

        self.input = open(input_file, 'r')
        self.output = open(output_file, 'a+')
        self.current_token = None
        self.current_token_position = 0
        self.comment = False

        self._tokenize()
        self.input.close()
        self.output.close()

    def _tokenize(self):
        """
            Iterates over each line of the .jack file
            and discovers it's tokens.
        """
        self.output.write("<tokens>\n")
        with self.input as file:
            for line in file:
                self.current_token_position = 0
                # Remove unnecessary whitespace
                line = " ".join(line.split())
                while self.hasMoreTokens(line):
                    self.advance(line)
        self.output.write("</tokens>")

    def _writeToFile(self):
        """
            Writes the current token to the output file.
        """
        token_type = self.tokenType(self.current_token)
        token_line = "<{0}> {1} </{0}>\n"
        token_value = ""

        if token_type == "KEYWORD":
            token_value = self.keyWord().lower()
        elif token_type == "SYMBOL":
            token_value = self.symbol()
            token_value = token_value.replace('&', '&amp;').replace('"', '&quot;')
            token_value = token_value.replace('<', '&lt;').replace('>', '&gt;')
        elif token_type == "IDENTIFIER":
            token_value = self.identifier()
        elif token_type == "INT_CONST":
            token_value = self.intVal()
        elif token_type == "STRING_CONST":
            token_value = self.stringVal()

        self.output.write(token_line.format(
            self.TOKEN_TYPES[token_type],
            token_value
        ))

    def _is_string(self, str_list):
        """
            Returns if an array of characters may be a string.
        """
        return len(str_list) > 0 and str_list[0] == '"'

    def _is_complete_string(self, str_list):
        """
            Returns if the string is complete inside the array of characters.
        """
        return len(str_list) > 1 and str_list[0] == '"' and str_list[-1] == '"'

    def hasMoreTokens(self, line):
        """
            Are there more tokens in the input?
            Return: boolean
        """
        return self.current_token_position <= (len(line) - 1)

    def advance(self, line):
        """
            Gets the next token from the input, and makes
            it the current token.
            This method should be called only if hasMoreTokens
            is True.
            Initially there is no current token.
        """
        current_token = []
        for index, letter in enumerate(line):
            if index >= self.current_token_position and not self.comment:
                if letter == " " and not self._is_string(current_token):
                    # Se a próxima letra for um espaço, o token acabou
                    # então escrevemos ele no arquivo
                    # No entanto, se houver um " no início, significa que é uma
                    # string e que pode conter espaço
                    self.current_token_position = index + 1
                    break
                elif letter == " " and self._is_string(current_token) \
                    and self._is_complete_string(current_token):
                    # Se for uma string, mas estiver completa, podemos escrever
                    # o token no arquivo
                    self.current_token_position = index + 1
                    break
                elif (index < len(line) -1) and \
                    letter == '/' and line[index + 1] == '/':
                    # Se começar um comentário de linha, devemos ir para a
                    # próxima linha então setamos o índice para o fim da linha
                    self.current_token_position = len(line)
                    break
                elif (index < len(line) -1) and \
                    letter == '/' and line[index + 1] == '*':
                    # Se começar um comentário de multiplas linhas, devemos
                    # avançar até o seu fim, e para isso encerrar o token
                    self.comment = True
                    break
                elif letter in self.SYMBOLS:
                    # Se a próxima letra for um símbolo, o token acabou
                    # então escrevemos ele no arquivo e depois escrevemos
                    # o símbolo
                    if len(current_token):
                        self.current_token = "".join(current_token)
                        self._writeToFile()

                    current_token = [letter]
                    self.current_token_position = index + 1
                    break
                elif index == (len(line) - 1):
                    # Se alcançamos a última letra da linha, o token acabou
                    # então escrevemos ele no arquivo
                    self.current_token_position = index + 1
                    break
                else:
                    # Caso contrário continuamos adicionando letras no token
                    current_token.append(letter)
                    self.current_token_position = index
            elif self.comment:
                if index < (len(line) - 1) and \
                    letter == '*' and line[index + 1] == '/':
                    self.comment = False
                    self.current_token_position = index + 2

                if index == (len(line) -1):
                    # Como o comentário permanece por mais de uma linha
                    # precisa pular de linha quando atinge o fim da atual
                    self.current_token_position = index + 1

        if len(current_token):
            self.current_token = "".join(current_token)
            self._writeToFile()

    def tokenType(self, token):
        """
            Returns the type of the current token, as a
            constant.
            Return: KEYWORD, SYMBOL, IDENTIFIER, INT_CONST,
            STRING_CONST
        """
        if token in self.KEYWORDS:
            return "KEYWORD"
        elif token in self.SYMBOLS:
            return "SYMBOL"
        elif token.startswith('"') and token.endswith('"'):
            return "STRING_CONST"
        else:
            try:
                int(token)
                return "INT_CONST"
            except:
                return "IDENTIFIER"

    def keyWord(self):
        """
            Returns the keyword which is the current token,
            as a constant.
            This method should be called only if tokenType is
            KEYWORD.
            Return: CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT,
            BOOLEAN, CHAR, VOID, VAR, STATIC, FIELD, LET, DO,
            IF, ELSE, WHILE, RETURN, TRUE, FALSE, NULL, THIS
        """
        return self.current_token.upper()

    def symbol(self):
        """
            Returns the character which is the current token.
            Should be called only if tokenType is SYMBOL.
            Return: char
        """
        return self.current_token

    def identifier(self):
        """
            Returns the identifier which is the current token.
            Should be called only if tokenType is IDENTIFIER.
            Return: string
        """
        return self.current_token

    def intVal(self):
        """
            Returns the integer value of the current token.
            Should be called only if tokenType is INT_CONST.
            Return: int
        """
        return self.current_token

    def stringVal(self):
        """
            Returns the string value of the current token,
            without the two enclosing double quotes.
            Should be called only if tokenType is STRING_CONST.
            Return: string
        """
        return self.current_token.replace('"', '')
