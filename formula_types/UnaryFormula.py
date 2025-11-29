from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula


class UnaryFormula(HybridSpatioTemporalFormula):
    """
    Class for unary formulas.
    """

    def __init__(self, op: str, operand: HybridSpatioTemporalFormula):
        self.op = op
        self.operand = operand

    def __repr__(self) -> str:
        return f"{self.op}({self.operand})"