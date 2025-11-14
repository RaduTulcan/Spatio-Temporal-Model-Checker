from HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from UnaryFormula import UnaryFormula


class Nom(HybridSpatioTemporalFormula):
    """
       Class for logical propositions.
    """

    def __init__(self, name: str):
        self.name: str = name

    def __repr__(self) -> str:
        return self.name

    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return self.name in grid[0][point[0]][point[1]]


class At(UnaryFormula):

    def __init__(self, name, op, operand):
        super().__init__(op, operand)
        self.name = name

    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        new_point: tuple[int, int] = (0, 0)

        # change the point w.r.t which the formula is evaluated
        for i in range(0, len(grid[0])):
            for j in range(0, len(grid[0][i])):
                if self.name in grid[0][i][j]:
                    new_point = (i, j)

        return self.operand.evaluate(grid, new_point)


class Bind(UnaryFormula):

    def __init__(self, name, op, operand):
        super().__init__(op, operand)
        self.name = name

    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        # bind the nominal to another spatial position
        for i in range(0, len(grid)):
            for j in range(0, len(grid[0])):
                for k in range(0, len(grid[0][i])):
                    if self.name in grid[i][j][k]:
                        grid[i][j][k].remove(self.name)

        for i in range(0, len(grid)):
            grid[i][point[0]][point[1]].append(self.name)

        return self.operand.evaluate(grid, point)
