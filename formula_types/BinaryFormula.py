from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula


class BinaryFormula(HybridSpatioTemporalFormula):
    """
    Class for binary operators.
    """

    def __init__(self, op: str, left: HybridSpatioTemporalFormula, right: HybridSpatioTemporalFormula):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"{self.left} {self.op} {self.right}"
