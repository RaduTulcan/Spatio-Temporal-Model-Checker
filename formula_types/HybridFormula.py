import copy
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula, memoize
from formula_types.UnaryFormula import UnaryFormula


class Nom(HybridSpatioTemporalFormula):
    """
       Class for logical propositions.
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return self.name

    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        return point == trace[time][self.name]


class At(UnaryFormula):
    """
       Class for hybrid at-formulas.
    """

    def __init__(self, name: str, op: str, operand: HybridSpatioTemporalFormula):
        super().__init__(op, operand)
        self.name = name
        self.operator_string = f"@{name}"

    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        return self.operand.evaluate_memoized(trace, time, trace[time][self.name], grid_size, memo)


class Bind(UnaryFormula):
    """
       Class for hybrid bind-formulas.
    """

    def __init__(self, name: str, op: str, operand: HybridSpatioTemporalFormula):
        super().__init__(op, operand)
        self.name = name
        self.operator_string = f"↓{name}"

    @memoize
    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple[HybridSpatioTemporalFormula, int], bool]) -> bool:
        new_trace: list[dict] = copy.deepcopy(trace)

        for i in range(0, len(new_trace)):
            new_trace[i][self.name] = point

        return self.operand.evaluate_memoized(new_trace, time, point, grid_size, memo)
