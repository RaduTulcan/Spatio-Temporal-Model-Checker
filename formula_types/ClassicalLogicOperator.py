from formula_types.UnaryOperator import UnaryOperator
from formula_types.BinaryOperator import BinaryOperator


class Verum:
    """
    Class for logical constant "true".
    """
    def __repr__(self):
        return "⊤"

    def evaluate(self, grid, point):
        return True


class Falsum:
    """
    Class for logical constant "false".
    """
    def __repr__(self):
        return "⊥"

    def evaluate(self, grid, point):
        return False


class Prop:
    """
       Class for logical propositions.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def evaluate(self, grid, point):
        return self.name in grid[0][point[0]][point[1]]


# --------------------------------------------------------------------------
# 1-ary operators
# --------------------------------------------------------------------------
class Not(UnaryOperator):
    """
       Class for logical negation.
    """
    def evaluate(self, grid, point):
        return not self.operand.evaluate(grid, point)


# --------------------------------------------------------------------------
# 1-ary operators
# --------------------------------------------------------------------------


class And(BinaryOperator):
    """
       Class for logical constant conjunction.
    """
    def evaluate(self, grid, point):
        return self.left.evaluate(grid, point) and self.right.evaluate(grid, point)

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"


class If(BinaryOperator):
    """
       Class for logical implication.
    """
    def evaluate(self, grid, point):
        return (not self.left.evaluate(grid, point)) or self.right.evaluate(grid, point)

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"


class Iff(BinaryOperator):
    """
       Class for logical bi-implication.
    """
    def evaluate(self, grid, point):
        return ((not self.left.evaluate(grid, point)) or self.right.evaluate(grid, point)) and (
                (not self.right.evaluate(grid, point)) or self.left.evaluate(grid, point))

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"


class Or(BinaryOperator):
    """
       Class for logical disjunction.
    """
    def evaluate(self, grid, point):
        return self.left.evaluate(grid, point) or self.right.evaluate(grid, point)

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"
