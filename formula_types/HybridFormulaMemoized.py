import copy

from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula, memoize
from formula_types.UnaryFormula import UnaryFormula

class Nom(HybridSpatioTemporalFormula):
    """
       Class for logical propositions.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def evaluate(self, trace, point):
        return self.evaluate_memoized(trace, 0, point, {})

    @memoize
    def evaluate_memoized(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return point == trace[0][self.name]


class At(UnaryFormula):
    """
       Class for hybrid at-formulas.
    """
    def __init__(self, name, op, operand):
        super().__init__(op, operand)
        self.name = name

    def evaluate(self, trace, point):
        return self.evaluate_memoized(trace, 0, point, {})

    @memoize
    def evaluate_memoized(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return self.operand.evaluate_memoized(trace, time, trace[0][self.name], memo)


class Bind(UnaryFormula):
    """
       Class for hybrid bind-formulas.
    """
    def __init__(self, name, op, operand):
        super().__init__(op, operand)
        self.name = name

    def evaluate(self, trace, point):
        return self.evaluate_memoized(trace, 0, point, {})

    @memoize
    def evaluate_memoized(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        copy_trace = copy.deepcopy(trace)

        for i in range(0, len(copy_trace)):
            copy_trace[i][self.name] = point

        return self.operand.evaluate_memoized(copy_trace, time, point, memo)