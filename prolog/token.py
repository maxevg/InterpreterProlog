from enum import Enum, auto

class Token:
    def __init__(self, token_type, lexeme, literal, line):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return self.lexeme

    def __repr__(self):
        return str(self)

class TokenType(Enum):
    ATOM = auto(),          # атом
    VARIABLE = auto(),      # переменная
    NUMBER = auto(),        # число
    LEFTSTAPLE = auto(),    # (
    RIGHTSTAPLE = auto(),   # )
    LEFTBRACKET = auto(),   # [
    RIGHTBRACKET = auto(),  # ]
    COLONMINUS = auto(),    # :-
    COMMA = auto(),         # ,
    DOT = auto(),           # .
    UNDERSCORE = auto(),    # _
    FAIL = auto(),          # fail
    WRITE = auto(),         # write
    NL = auto(),            # \n
    TAB = auto(),           # \t
    IS = auto(),            # is
    PLUS = auto(),          # +
    MINUS = auto(),         # -
    SLASH = auto(),         # /
    STAR = auto(),          # *
    GREATER = auto(),       # >
    LESS = auto(),          # <
    GREATEREQUAL = auto(),  # >=
    EQUALLESS = auto(),     # =<
    EQUALEQUAL = auto(),    # ==
    EQUALSLASH = auto(),    # =/
    RETRACT = auto(),       # retract
    ASSERTA = auto(),       # asserta
    ASSERTZ = auto(),       # assertz
    CUT = auto(),           # !
    BAR = auto(),           # |
    EOF = auto()            # конец для считывания