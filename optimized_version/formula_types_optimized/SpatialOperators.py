from UnaryFormula import UnaryOperator


class Front(UnaryOperator):
    """
       Class for spatial front operator.
    """
    def evaluate(self, grid, point):
        return self.operand.evaluate(grid, (point[0] - 1, point[1]))


class Back(UnaryOperator):
    """
        Class for spatial back operator.
    """
    def evaluate(self, grid, point):
        return self.operand.evaluate(grid, (point[0] + 1, point[1]))


class Left(UnaryOperator):
    """
        Class for spatial left operator.
    """
    def evaluate(self, grid, point):
        return self.operand.evaluate(grid, (point[0], point[1] - 1))


class Right(UnaryOperator):
    """
        Class for spatial right operator.
    """
    def evaluate(self, grid, point):
        return self.operand.evaluate(grid, (point[0], point[1] + 1))
