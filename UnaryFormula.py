from HybridSpatioTemporalFormula import HybridSpatioTemporalFormula


class UnaryFormula(HybridSpatioTemporalFormula):
    """
    Class for unary formulas.
    """
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f"{self.op}({self.operand})"