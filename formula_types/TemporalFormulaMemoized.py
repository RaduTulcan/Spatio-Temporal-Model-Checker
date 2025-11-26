from formula_types.UnaryFormula import UnaryFormula
from formula_types.BinaryFormula import BinaryFormula
from formula_types.HybridSpatioTemporalFormula import memoize


class Next(UnaryFormula):
    """
        Class for temporal next operator.
    """

    def evaluate(self, trace, point):
        return self.evaluate_memoized(trace, 0, point, {})

    @memoize
    def evaluate_memoized(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        if time+1 >= len(trace):
            return False
        else:
            return self.operand.evaluate_memoized(trace, time+1, point, memo)


class Eventually(UnaryFormula):
    """
        Class for temporal eventually operator.
    """

    def evaluate(self, trace, point):
        return self.evaluate_memoized(trace, 0, point, {})

    @memoize
    def evaluate_memoized(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        if time == len(trace) - 1:
            return self.operand.evaluate_memoized(trace, time, point, memo)
        else:
            return self.operand.evaluate_memoized(trace, time, point, memo) or self.evaluate_memoized(trace, time+1, point, memo) 



class Always(UnaryFormula):
    """
        Class for temporal always operator.
    """

    def evaluate(self, trace, point):
        return self.evaluate_memoized(trace, 0, point, {})

    @memoize
    def evaluate_memoized(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        if time == len(trace) - 1:
            return self.operand.evaluate_memoized(trace, time, point, memo)
        else:
            return self.operand.evaluate_memoized(trace, time, point, memo) and self.evaluate_memoized(trace, time+1, point, memo)


class Until(BinaryFormula):
    """
        Class for temporal until operator.
    """

    def evaluate(self, trace, point):
        return self.evaluate_memoized(trace, 0, point, {})

    @memoize
    def evaluate_memoized(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        result = self.right.evaluate_memoized(trace, time, point, memo)
        if not result and time < len(trace)-1:
            result = self.left.evaluate_memoized(trace, time, point, memo) and self.evaluate_memoized(trace, time+1, point, memo)
        return result