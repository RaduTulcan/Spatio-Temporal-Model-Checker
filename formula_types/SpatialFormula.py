from formula_types.UnaryFormula import UnaryFormula
from formula_types.HybridSpatioTemporalFormula import memoize, HybridSpatioTemporalFormula


class Front(UnaryFormula):
    """
       Class for spatial front operator.
    """
    def __init__(self, op, operand):
        super().__init__(op, operand)
        self.operator_string = "Front"

    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        if 0 <= point[0] - 1 < grid_size[0] and 0 <= point[1] < grid_size[1]:
            return self.operand.evaluate_memoized(trace, time, (point[0] - 1, point[1]), grid_size, memo)
        else:
            return False


class Back(UnaryFormula):
    """
        Class for spatial back operator.
    """
    def __init__(self, op, operand):
        super().__init__(op, operand)
        self.operator_string = "Back"

    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        if 0 <= point[0] + 1 < grid_size[0] and 0 <= point[1] < grid_size[1]:
            return self.operand.evaluate_memoized(trace, time, (point[0] + 1, point[1]), grid_size, memo)
        else:
            return False


class Left(UnaryFormula):
    """
        Class for spatial left operator.
    """
    def __init__(self, op, operand):
        super().__init__(op, operand)
        self.operator_string = "Left"

    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        if 0 <= point[0] < grid_size[0] and 0 <= point[1] - 1 < grid_size[1]:
            return self.operand.evaluate_memoized(trace, time, (point[0], point[1] - 1), grid_size, memo)
        else:
            return False


class Right(UnaryFormula):
    """
        Class for spatial right operator.
    """
    def __init__(self, op, operand):
        super().__init__(op, operand)
        self.operator_string = "Right"

    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        if 0 <= point[0] < grid_size[0] and 0 <= point[1] + 1 < grid_size[1]:
            return self.operand.evaluate_memoized(trace, time, (point[0], point[1] + 1), grid_size, memo)
        else:
            return False
