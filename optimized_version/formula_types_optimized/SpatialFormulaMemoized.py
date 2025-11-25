from UnaryFormula import UnaryFormula
from HybridSpatioTemporalFormula import memoized_evaluate


class Front(UnaryFormula):
    """
       Class for spatial front operator.
    """
    @memoized_evaluate
    def evaluate(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return self.operand.evaluate(trace, time, (point[0] - 1, point[1]), memo)


class Back(UnaryFormula):
    """
        Class for spatial back operator.
    """
    @memoized_evaluate
    def evaluate(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return self.operand.evaluate(trace, time, (point[0] + 1, point[1]), memo)


class Left(UnaryFormula):
    """
        Class for spatial left operator.
    """
    def evaluate(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return self.operand.evaluate(trace, time, (point[0], point[1] - 1), memo)


class Right(UnaryFormula):
    """
        Class for spatial right operator.
    """
    def evaluate(self, trace,time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        return self.operand.evaluate(trace, time, (point[0], point[1] + 1), memo)
