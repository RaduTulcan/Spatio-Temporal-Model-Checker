from formula_types.UnaryOperator import UnaryOperator
from formula_types.BinaryOperator import BinaryOperator


class Verum:
    def __repr__(self):
        return "⊤"

    def evaluate(self, grid, point):
        return True


class Falsum:
    def __repr__(self):
        return "⊥"

    def evaluate(self, grid, point):
        return False


class Prop:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def evaluate(self, grid, point):
        return self.name in grid[point[0]][point[1]]


# --------------------------------------------------------------------------
# 1-ary operators
# --------------------------------------------------------------------------
class Not(UnaryOperator):
    def evaluate(self, grid, point):
        return not self.operand.evaluate(grid, point)


# --------------------------------------------------------------------------
# 1-ary operators
# --------------------------------------------------------------------------


class And(BinaryOperator):
    def evaluate(self, grid, point):
        return self.left.evaluate(grid, point) and self.right.evaluate(grid, point)

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"


class If(BinaryOperator):
    def evaluate(self, grid, point):
        return (not self.left.evaluate(grid, point)) or self.right.evaluate(grid, point)

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

class Iff(BinaryOperator):
    def evaluate(self, grid, point):
        return ((not self.left.evaluate(grid, point)) or self.right.evaluate(grid, point)) and (
                (not self.right.evaluate(grid, point)) or self.left.evaluate(grid, point))

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

class Or(BinaryOperator):
    def evaluate(self, grid, point):
        return self.left.evaluate(grid, point) or self.right.evaluate(grid, point)

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"
