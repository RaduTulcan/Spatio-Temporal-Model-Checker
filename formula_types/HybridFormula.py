import copy
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from formula_types.UnaryFormula import UnaryFormula


class Nom(HybridSpatioTemporalFormula):
    """
       Class for logical propositions.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def evaluate(self, grid, point):
        return point == grid[0][self.name]


class At(UnaryFormula):
    """
       Class for hybrid at-formulas.
    """
    def __init__(self, name, op, operand):
        super().__init__(op, operand)
        self.name = name


    def evaluate(self, grid, point):
        return self.operand.evaluate(grid, grid[0][self.name])


class Bind(UnaryFormula):
    """
       Class for hybrid bind-formulas.
    """
    def __init__(self, name, op, operand):
        super().__init__(op, operand)
        self.name = name

    def evaluate(self, grid, point):
        copy_grid = copy.deepcopy(grid)

        for i in range(0, len(copy_grid)):
            copy_grid[i][self.name] = point

        return self.operand.evaluate(copy_grid, point)