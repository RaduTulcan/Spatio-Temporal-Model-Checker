
class SpatialFormula:
    pass


class UnaryFormula(SpatialFormula):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f"{self.op}({self.operand})"


class BinaryFormula(SpatialFormula):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"


# --------------------------------------------------------------------------
# 0-ary formulas
# --------------------------------------------------------------------------
class Verum(SpatialFormula):
    def __repr__(self):
        return "⊤"

    def evaluate(self, grid, point):
        return True


class Falsum(SpatialFormula):
    def __repr__(self):
        return "⊥"

    def evaluate(self, grid, point):
        return False


class Prop(SpatialFormula):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def evaluate(self, grid, point):
        return self.name in grid[point[0]][point[1]]


# --------------------------------------------------------------------------
# 1-ary formulas
# --------------------------------------------------------------------------
class Front(UnaryFormula):

    def evaluate(self, grid, point):
        if point[0] == 0:
            return False
        else:
            return self.operand.evaluate(grid, (point[0] - 1, point[1]))


class Back(UnaryFormula):
    def evaluate(self, grid, point):
        if point[0] == len(grid) - 1:
            return False
        else:
            return self.operand.evaluate(grid, (point[0] + 1, point[1]))


class Left(UnaryFormula):
    def evaluate(self, grid, point):
        if point[1] == 0:
            return False
        else:
            return self.operand.evaluate(grid, (point[0], point[1] - 1))


class Right(UnaryFormula):
    def evaluate(self, grid, point):
        if point[1] == len(grid[point[0]]) - 1:
            return False
        else:
            return self.operand.evaluate(grid, (point[0], point[1] + 1))


class Not(UnaryFormula):
    def evaluate(self, grid, point):
        return not self.operand.evaluate(grid, point)



# --------------------------------------------------------------------------
# 2-ary formulas
# --------------------------------------------------------------------------
class And(BinaryFormula):
    def evaluate(self, grid, point):
        return self.left.evaluate(grid, point) and self.right.evaluate(grid, point)


class If(BinaryFormula):
    def evaluate(self, grid, point):
        return (not self.left.evaluate(grid, point)) or self.right.evaluate(grid, point)


class Iff(BinaryFormula):
    def evaluate(self, grid, point):
        return ((not self.left.evaluate(grid, point)) or self.right.evaluate(grid, point)) and (
                    (not self.right.evaluate(grid, point)) or self.left.evaluate(grid, point))


class Or(BinaryFormula):

    def evaluate(self, grid, point):
        return self.left.evaluate(grid, point) or self.right.evaluate(grid, point)
