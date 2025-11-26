from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula


class BinaryFormula(HybridSpatioTemporalFormula):
    """
    Class for binary operators.
    """

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"