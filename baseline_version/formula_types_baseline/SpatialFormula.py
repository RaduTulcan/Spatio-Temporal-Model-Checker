from UnaryFormula import UnaryFormula


class Front(UnaryFormula):
    """
       Class for spatial front operator.
    """
    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return self.operand.evaluate(grid, (point[0] - 1, point[1]))


class Back(UnaryFormula):
    """
        Class for spatial back operator.
    """
    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return self.operand.evaluate(grid, (point[0] + 1, point[1]))


class Left(UnaryFormula):
    """
        Class for spatial left operator.
    """
    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return self.operand.evaluate(grid, (point[0], point[1] - 1))


class Right(UnaryFormula):
    """
        Class for spatial right operator.
    """
    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return self.operand.evaluate(grid, (point[0], point[1] + 1))
