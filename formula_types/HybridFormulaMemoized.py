import copy

from HybridSpatioTemporalFormula import HybridSpatioTemporalFormula, memoized_evaluate
from UnaryFormula import UnaryFormula

class Nom(HybridSpatioTemporalFormula):
    """
       Class for logical propositions.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    @memoized_evaluate
    def evaluate(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return point == trace[0][self.name]


class At(UnaryFormula):
    """
       Class for hybrid at-formulas.
    """
    def __init__(self, name, op, operand):
        super().__init__(op, operand)
        self.name = name

    @memoized_evaluate
    def evaluate(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return self.operand.evaluate(trace, time, trace[0][self.name], memo)


class Bind(UnaryFormula):
    """
       Class for hybrid bind-formulas.
    """
    def __init__(self, name, op, operand):
        super().__init__(op, operand)
        self.name = name

    @memoized_evaluate
    def evaluate(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        copy_trace = copy.deepcopy(trace)

        for i in range(0, len(copy_trace)):
            copy_trace[i][self.name] = point

        return self.operand.evaluate(copy_trace, time, point, memo)