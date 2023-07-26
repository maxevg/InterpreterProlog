from .expression import Visitor


class MathInterpreter(Visitor):

    def evaluate_expr(self, expr):
        return expr.accept(self)

    def compute_binary_operand(self, left, operand, right):
        if type(left) != type(right):
            raise Exception(f'left {left} and right {right} operand must have the same type')
        if operand == '*':
            return left.multiply(right)
        elif operand == '/':
            return left.divide(right)
        elif operand == '+':
            return left.add(right)
        elif operand == '-':
            return left.substract(right)
        else:
            raise Exception(f'Invalid binary operand {operand}')

    def visit_binary(self, expr):
        left = self.evaluate_expr(expr.left)
        right = self.evaluate_expr(expr.right)

        return self.compute_binary_operand(left, expr.operand, right)

    def visit_primary(self, expr):
        return expr.exp


class LogicInterpreter(Visitor):

    def evaluate_expr(self, expr):
        return expr.accept(self)

    def compute_binary_operand(self, left, operand, right):
        if type(left) != type(right):
            raise Exception(f'left {left} and right {right} operand must have the same type')
        if operand == '==':
            return left.equal(right)
        elif operand == '=/':
            return left.not_equal(right)
        elif operand == '=<':
            return left.equal_less(right)
        elif operand == '<':
            return left.less(right)
        elif operand == '>=':
            return left.greater_equal(right)
        elif operand == '>':
            return left.greater(right)
        else:
            raise Exception(f'Invalid binary operand {operand}')

    def visit_binary(self, expr):
        left = self.evaluate_expr(expr.left)
        right = self.evaluate_expr(expr.right)

        return self.compute_binary_operand(left, expr.operand, right)

    def visit_primary(self, expr):
        return expr.exp