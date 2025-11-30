from formula_types.UnaryFormula import UnaryFormula
from formula_types.BinaryFormula import BinaryFormula
from formula_types.HybridSpatioTemporalFormula import memoize, HybridSpatioTemporalFormula


class Next(UnaryFormula):
    """
        Class for temporal next operator.
    """

    def __init__(self, op, operand):
        super().__init__(op, operand)
        self.operator_string = "X"

    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        if time + 1 >= len(trace):
            return False
        else:
            return self.operand.evaluate_memoized(trace, time + 1, point, grid_size, memo)


class Eventually(UnaryFormula):
    """
        Class for temporal eventually operator.
    """
    def __init__(self, op, operand):
        super().__init__(op, operand)
        self.operator_string = "F"

    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        if time == len(trace) - 1:
            return self.operand.evaluate_memoized(trace, time, point, grid_size, memo)
        else:
            return self.operand.evaluate_memoized(trace, time, point, grid_size, memo) or self.evaluate_memoized(trace,
                                                                                                                 time + 1,
                                                                                                                 point,
                                                                                                                 grid_size,
                                                                                                                 memo)


class Always(UnaryFormula):
    """
        Class for temporal always operator.
    """
    def __init__(self, op, operand):
        super().__init__(op, operand)
        self.operator_string = "G"

    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        if time == len(trace) - 1:
            return self.operand.evaluate_memoized(trace, time, point, grid_size, memo)
        else:
            return self.operand.evaluate_memoized(trace, time, point, grid_size, memo) and self.evaluate_memoized(trace,
                                                                                                                  time + 1,
                                                                                                                  point,
                                                                                                                  grid_size,
                                                                                                                  memo)


class Until(BinaryFormula):
    """
        Class for temporal until operator.
    """
    def __init__(self, op, left, right):
        super().__init__(op, left, right)
        self.operator_string = "U"

    # recursive version (faster, but hits recursion limit for very long traces)
    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        if self.right.evaluate_memoized(trace, time, point, grid_size, memo):
            return True
        elif time < len(trace) - 1:
            return self.left.evaluate_memoized(trace, time, point, grid_size, memo) and self.evaluate_memoized(trace,
                                                                                                               time + 1,
                                                                                                               point,
                                                                                                               grid_size,
                                                                                                               memo)
        else:
            return False
