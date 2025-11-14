from UnaryFormula import UnaryOperator


class Nom:
    """
       Class for logical propositions.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def evaluate(self, grid, point):
        return point == grid[0][self.name]


class At(UnaryOperator):

    def __init__(self, name, op, operand):
        super().__init__(op, operand)
        self.name = name


    def evaluate(self, grid, point):
        return self.operand.evaluate(grid, grid[0][self.name])


class Bind(UnaryOperator):

    def __init__(self, name, op, operand):
        super().__init__(op, operand)
        self.name = name

    def evaluate(self, grid, point):
        grid[0][self.name] = point
        return self.operand.evaluate(grid, point)