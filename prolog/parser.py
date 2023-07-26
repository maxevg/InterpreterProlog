from .token import TokenType
from .interpreter import Conjunction, Rule
from .types import Arithmetic, Logic, Variable, Term, TRUE, Number, Dot, Bar
from .builtins import Fail, Write, Nl, Tab, Retract, AssertA, AssertZ, Cut
from .expression import BinaryExpression, PrimaryExpression


def default_error_handler(line, message):
    print(f'Line[{line}] Error: {message}')
    raise Exception('Parser error')


def is_single_param_buildin(token_type):
    st = set([TokenType.RETRACT, TokenType.ASSERTA, TokenType.ASSERTZ])
    if token_type in st:
        return True
    return False


class Parser:
    def __init__(self, tokens, report=default_error_handler):
        self.current_token = 0
        self.check_done = False
        self.scope = {}
        self.tokens = tokens
        self._report = report

    def peek(self):
        return self.tokens[self.current_token]

    def peek_next(self):
        return self.tokens[self.current_token + 1]

    def check_end(self):
        return self.peek().token_type == TokenType.EOF

    def check_previous(self):
        return self.tokens[self.current_token - 1]

    def advance(self):
        self.current_token += 1
        if self.check_end():
            self.check_done = True
        return self.check_previous()

    def token_match(self, token_type):
        if isinstance(token_type, list):
            return self.peek().token_type in token_type
        return self.peek().token_type == token_type

    def next_token_match(self, token_type):
        if isinstance(token_type, list):
            return self.peek_next().token_type in token_type
        return self.peek_next().token_type == token_type

    def check_type(self, token, token_type):
        return token.token_type == token_type

    def create_variable(self, name, has_arithmetic_exp=None):
        variable = self.scope.get(name, None)
        if variable is None:
            if has_arithmetic_exp is None:
                variable = Variable(name)
            else:
                variable = Arithmetic(name, has_arithmetic_exp)
            self.scope[name] = variable
        elif isinstance(variable, Variable) and has_arithmetic_exp is not None:
            variable = Arithmetic(name, has_arithmetic_exp)
        return variable

    def parse_primary(self):
        token = self.peek()

        if self.check_type(token, TokenType.NUMBER):
            self.advance()
            number_value = token.literal
            return PrimaryExpression(Number(number_value))
        elif self.check_type(token, TokenType.VARIABLE):
            self.advance()
            return PrimaryExpression(
                self.create_variable(token.lexeme)
            )
        elif self.check_type(token, TokenType.LEFTSTAPLE):
            self.advance()
            expr = self.parse_expression()

            prev_token = self.advance()  # consume ')'
            if prev_token.token_type != TokenType.RIGHTSTAPLE:
                self._report(
                    self.peek().line,
                    f'Expected ")" after expression: {expr}'
                )
            return expr

        self._report(
            self.peek().line,
            f'Expected number or variable but got: {token}'
        )

    def parse_equality(self):
        expr = self.parse_comperison()
        while self.token_match(
            [TokenType.EQUALEQUAL, TokenType.EQUALSLASH]
        ):
            self.advance()
            operator = self.check_previous().lexeme
            right = self.parse_comperison()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def parse_comperison(self):
        expr = self.parse_addition()

        while self.token_match([
            TokenType.GREATER,
            TokenType.GREATEREQUAL,
            TokenType.LESS,
            TokenType.EQUALLESS
        ]):
            self.advance()
            operator = self.check_previous().lexeme
            right = self.parse_addition()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def parse_addition(self):
        expr = self.parse_multiplication()

        while self.token_match([TokenType.MINUS, TokenType.PLUS]):
            self.advance()
            operator = self.check_previous().lexeme
            right = self.parse_multiplication()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def parse_multiplication(self):
        expr = self.parse_primary()

        while self.token_match([TokenType.SLASH, TokenType.STAR]):
            self.advance()
            operator = self.check_previous().lexeme
            right = self.parse_primary()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def parse_expression(self):
        return self.parse_equality()

    def parse_arithmetic(self, token):
        self.advance()
        return self.create_variable(
            token.lexeme,
            self.parse_expression()
        )

    def parse_logic(self):
        return Logic(self.parse_equality())

    def parse_atom(self):
        token = self.peek()
        if not self.token_match([
            TokenType.VARIABLE,
            TokenType.UNDERSCORE,
            TokenType.NUMBER,
            TokenType.FAIL,
            TokenType.WRITE,
            TokenType.NL,
            TokenType.TAB,
            TokenType.RETRACT,
            TokenType.ASSERTA,
            TokenType.ASSERTZ,
            TokenType.CUT,
            TokenType.ATOM
        ]):
            self._report(token.line, f'Bad atom name: {token.lexeme}')

        if self.check_type(token, TokenType.NUMBER):
            if self.peek_next().token_type == TokenType.COLONMINUS or \
               self.peek_next().token_type == TokenType.DOT or \
               self.peek_next().token_type == TokenType.LEFTSTAPLE:
                self._report(
                    self.peek().line,
                    f'Number cannot be a rule: {self.peek()}'
                )

        self.advance()
        return token

    def parse_buildin_single_arg(self, predicate, args):
        if len(args) != 1:
            self._report(
                self.peek().line,
                f'{predicate} requires exactly one argument'
            )
        if predicate == 'retract':
            return Retract(args[0])
        if predicate == 'asserta':
            return AssertA(args[0])
        if predicate == 'assertz':
            return AssertZ(args[0])

    def parse_list(self):
        dot_list = []
        dot_tail = None
        self.advance()
        while not self.token_match(TokenType.RIGHTBRACKET):
            if self.token_match(TokenType.BAR):
                dot_tail = []
                self.advance()
                continue

            list_term = None
            if self.token_match(TokenType.LEFTBRACKET):
                list_term = self.parse_list()
            else:
                list_term = self.parse_term()

            if dot_tail is not None:
                dot_tail = list_term
            else:
                dot_list.append(list_term)
            if self.token_match(TokenType.COMMA):
                self.advance()
        self.advance()

        if dot_tail is None:
            return Dot.from_list(dot_list)

        return Bar(
            Dot.from_list(dot_list),
            dot_tail
        )

    def parse_term(self):
        if self.token_match(TokenType.LEFTSTAPLE):
            self.advance()
            args = []
            while not self.token_match(TokenType.RIGHTSTAPLE):
                args.append(self.parse_term())
                if not self.token_match(TokenType.COMMA) and \
                   not self.token_match(TokenType.RIGHTSTAPLE):
                    self._report(
                        self.peek().line,
                        f'Expecter , or ) in term but got {self.peek()}')
                if self.token_match(TokenType.COMMA):
                    self.advance()

            self.advance()
            return Conjunction(args)

        if self.next_token_match([
            TokenType.EQUALEQUAL,
            TokenType.EQUALSLASH,
            TokenType.EQUALLESS,
            TokenType.LESS,
            TokenType.GREATEREQUAL,
            TokenType.GREATER
        ]):
            return self.parse_logic()

        if self.token_match(TokenType.LEFTBRACKET):
            return self.parse_list()

        token = self.parse_atom()
        predicate = token.lexeme
        if self.check_type(token, TokenType.VARIABLE) or \
           self.check_type(token, TokenType.UNDERSCORE):
            if self.check_type(token, TokenType.UNDERSCORE):
                return Variable('_')

            if self.check_type(token, TokenType.VARIABLE):
                if self.peek().token_type == TokenType.IS:
                    return self.parse_arithmetic(token)

            return self.create_variable(predicate)

        if self.check_type(token, TokenType.FAIL):
            return Fail()

        if self.check_type(token, TokenType.CUT):
            return Cut()

        if self.check_type(token, TokenType.NL):
            return Nl()

        if self.check_type(token, TokenType.TAB):
            return Tab()

        if self.check_type(token, TokenType.NUMBER):
            number_value = token.literal
            return Number(number_value)

        if not self.token_match(TokenType.LEFTSTAPLE):
            return Term(predicate)

        self.advance()
        args = []
        while not self.token_match(TokenType.RIGHTSTAPLE):
            args.append(self.parse_term())
            if not self.token_match(TokenType.COMMA) and \
               not self.token_match(TokenType.RIGHTSTAPLE):
                self._report(
                    self.peek().line,
                    f'Expected , or ) in term but got {self.peek()}')

            if self.token_match(TokenType.COMMA):
                self.advance()

        self.advance()

        if is_single_param_buildin(token.token_type):
            return self.parse_buildin_single_arg(predicate, args)

        if self.check_type(token, TokenType.WRITE):
            return Write(*args)

        return Term(predicate, *args)

    def parse_rule(self):
        head = self.parse_term()
        if self.token_match(TokenType.DOT):
            self.advance()
            return Rule(head, TRUE())

        if not self.token_match(TokenType.COLONMINUS):
            self._report(
                self.peek().line,
                f'Expected :- in rule but got {self.peek()}')

        self.advance()
        args = []
        while not self.token_match(TokenType.DOT):
            args.append(self.parse_term())
            #print(args)
            if not self.token_match(TokenType.COMMA) and \
               not self.token_match(TokenType.DOT):
                self._report(
                    self.peek().line,
                    f'Expected , or . in term but got {self.peek()}')

            if self.token_match(TokenType.COMMA):
                self.advance()

        self.advance()
        body = None
        if len(args) == 1:
            body = args[0]
        else:
            body = Conjunction(args)
        return Rule(head, body)

    def _all_vars(self, terms):
        variables = []
        for term in terms:
            if isinstance(term, Term):
                for arg in term.args:
                    if isinstance(arg, Variable):
                        if arg not in variables:
                            variables.append(arg)
        return variables

    def parse_query(self):
        self.scope = {}
        head = self.parse_term()

        if self.token_match(TokenType.DOT):
            self.advance()
            return head

        if self.token_match(TokenType.COLONMINUS):
            self._report(
                self.peek().line,
                'Cannot use rule as a query')

        self.advance()
        args = [head]
        while not self.token_match(TokenType.DOT):
            args.append(self.parse_term())
            if not self.token_match(TokenType.COMMA) and \
               not self.token_match(TokenType.DOT):
                self._report(
                    self.peek().line,
                    f'Expected , or . in term but got {self.peek()}')

            if self.token_match(TokenType.COMMA):
                self.advance()

        self.advance()

        head = Term('##')
        vars = self._all_vars(args)
        if len(vars) > 0:
            head = Term('##', *vars)

        return Rule(head, Conjunction(args))

    def parse(self):
        rules = []
        while not self.check_done:
            self.scope = {}
            rules.append(self.parse_rule())
        return rules
