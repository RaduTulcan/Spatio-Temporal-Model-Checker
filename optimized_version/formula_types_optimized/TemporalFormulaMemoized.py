from UnaryFormula import UnaryFormula
from BinaryFormula import BinaryFormula
from HybridSpatioTemporalFormula import memoized_evaluate


class Next(UnaryFormula):
    """
        Class for temporal next operator.
    """
    @memoized_evaluate
    def evaluate(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        if time+1 >= len(trace):
            return False
        else:
            return self.operand.evaluate(trace, time+1, point, memo)


class Eventually(UnaryFormula):
    """
        Class for temporal eventually operator.
    """
    @memoized_evaluate
    def evaluate(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        if time == len(trace) - 1:
            return self.operand.evaluate(trace, time, point, memo)
        else:
            return self.operand.evaluate(trace, time, point, memo) or self.evaluate(trace, time+1, point, memo) 



class Always(UnaryFormula):
    """
        Class for temporal always operator.
    """

    @memoized_evaluate
    def evaluate(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        if time == len(trace) - 1:
            return self.operand.evaluate(trace, time, point, memo)
        else:
            return self.operand.evaluate(trace, time, point, memo) and self.evaluate(trace, time+1, point, memo)


class Until(BinaryFormula):
    """
        Class for temporal until operator.
    """
    @memoized_evaluate
    def evaluate(self, trace, time, point, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        result = self.right.evaluate(trace, time, point, memo)
        if not result and time < len(trace)-1:
            result = self.left.evaluate(trace, time, point, memo) and self.evaluate(trace, time+1, point, memo)
        return result