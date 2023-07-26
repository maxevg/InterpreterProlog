from .token import Token, TokenType


def default_error_handler(line, message):
    print(f'Line[{line}] Error: {message}')
    raise Exception('Scanner error')


def initialize_keywords():
    keywords = {
        'fail': TokenType.FAIL,
        'write': TokenType.WRITE,
        'nl': TokenType.NL,
        'tab': TokenType.TAB,
        'is': TokenType.IS,
        'retract': TokenType.RETRACT,
        'asserta': TokenType.ASSERTA,
        'assertz': TokenType.ASSERTZ
    }
    return keywords


class Scanner:
    def __init__(self, data, report=default_error_handler):
        self.data = data
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.report = report
        self.keywords = initialize_keywords()

    def add_token(self, token_type):
        self.add_token_with_literal(token_type, None)

    def add_token_with_literal(self, token_type, literal, lex=None):
        lexeme = self.data[self.start:self.current] if lex is None \
            else lex
        self.tokens.append(
            Token(
                token_type,
                lexeme,
                literal,
                self.line
            )
        )

    def check_end(self):
        return self.current >= len(self.data)

    def check_next(self, expected):
        if self.check_end():
            return False

        if self.data[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self):
        if self.check_end():
            return '\0'
        return self.data[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.data):
            return '\0'
        return self.data[self.current + 1]

    def alphanum_underscore(self, char):
        return (char.isalnum()) or (char == '_')

    def check_keyword(self):
        value = self.data[self.start:self.current]
        token_type = self.keywords.get(value, TokenType.ATOM)
        return token_type

    def complete_atom(self):
        while self.alphanum_underscore(self.peek()):
            self.current += 1

        token_type = self.check_keyword()
        self.add_token(token_type)

    def complete_variable(self):
        while self.alphanum_underscore(self.peek()):
            self.current += 1

        self.add_token(TokenType.VARIABLE)

    def complete_number(self):
        while self.peek().isdigit():
            self.current += 1

        if self.peek() == '.' and self.peek_next().isdigit():
            self.current += 1
            while self.peek().isdigit():
                self.current += 1

        value = float(self.data[self.start:self.current])
        self.add_token_with_literal(TokenType.NUMBER, value)

    def complete_string(self):
        while self.peek() != "'" and not self.check_end():
            if self.peek() == '\n':
                self.line += 1
            self.current += 1

        if self.check_end():
            self.report(self.line, 'Unterminated string')

        self.current += 1
        literal = self.data[self.start+1:self.current-1]
        self.add_token_with_literal(TokenType.ATOM, literal, literal)

    def scan_token(self):
        char = self.data[self.current]
        self.current += 1

        if char.isspace():
            pass
        elif char == '\n':
            self.line += 1
        elif char == '%':
            while not self.peek() == '\n' and \
                  not self.check_end():
                self.current += 1
        elif char == '/' and self.check_next('*'):
            while not self.check_end():
                char = self.data[self.current]
                self.current += 1
                if char == '*' and self.check_next('/'):
                    break
                if self.check_end():
                    self.report(self.line, 'Unterminated comment')
        elif char == "'":
            self.complete_string()
        elif char.islower():
            self.complete_atom()
        elif char == '_':
            if not self.alphanum_underscore(self.peek_next()):
                self.add_token(TokenType.UNDERSCORE)
            else:
                self.complete_variable()
        elif char.isupper():
            self.complete_variable()
        elif char == '-' and self.peek().isdigit():
            self.complete_number()
        elif char.isdigit():
            self.complete_number()
        elif char == '[':
            self.add_token(TokenType.LEFTBRACKET)
        elif char == ']':
            self.add_token(TokenType.RIGHTBRACKET)
        elif char == '|':
            self.add_token(TokenType.BAR)
        elif char == '!':
            self.add_token(TokenType.CUT)
        elif char == '(':
            self.add_token(TokenType.LEFTSTAPLE)
        elif char == ')':
            self.add_token(TokenType.RIGHTSTAPLE)
        elif char == '*':
            self.add_token(TokenType.STAR)
        elif char == '/':
            self.add_token(TokenType.SLASH)
        elif char == '+':
            self.add_token(TokenType.PLUS)
        elif char == '-':
            self.add_token(TokenType.MINUS)
        elif char == '=' and self.check_next('='):
            self.add_token(TokenType.EQUALEQUAL)
        elif char == '=' and self.check_next('/'):
            self.add_token(TokenType.EQUALSLASH)
        elif char == '=' and self.check_next('<'):
            self.add_token(TokenType.EQUALLESS)
        elif char == '<':
            self.add_token(TokenType.LESS)
        elif char == '>' and self.check_next('='):
            self.add_token(TokenType.GREATEREQUAL)
        elif char == '>':
            self.add_token(TokenType.GREATER)
        elif char == ':':
            if self.check_next('-'):
                self.add_token(TokenType.COLONMINUS)
            else:
                self.report(self.line, f'Expected `-` but found `{char}`')
        elif char == '.':
            self.add_token(TokenType.DOT)
        elif char == ',':
            self.add_token(TokenType.COMMA)
        else:
            self.report(self.line, f'Unexpected character: {char}')

    def tokenize(self):
        while self.check_end() is not True:
            self.start = self.current
            self.scan_token()

        self.add_token(TokenType.EOF)
        return self.tokens
