from formula_types.UnaryFormula import UnaryFormula
from formula_types.HybridSpatioTemporalFormula import memoize


class Front(UnaryFormula):
    """
       Class for spatial front operator.
    """
    @memoize
    def evaluate_memoized(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return self.operand.evaluate_memoized(trace, time, (point[0] - 1, point[1]), memo)


class Back(UnaryFormula):
    """
        Class for spatial back operator.
    """
    @memoize
    def evaluate_memoized(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return self.operand.evaluate_memoized(trace, time, (point[0] + 1, point[1]), memo)


class Left(UnaryFormula):
    """
        Class for spatial left operator.
    """
    def evaluate_memoized(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return self.operand.evaluate_memoized(trace, time, (point[0], point[1] - 1), memo)


class Right(UnaryFormula):
    """
        Class for spatial right operator.
    """
    def evaluate_memoized(self, trace,time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return self.operand.evaluate_memoized(trace, time, (point[0], point[1] + 1), memo)
