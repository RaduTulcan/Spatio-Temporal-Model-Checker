from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula


class BinaryFormula(HybridSpatioTemporalFormula):
    """
    Class for binary operators.
    """

    def __init__(self, op: str, left: HybridSpatioTemporalFormula, right: HybridSpatioTemporalFormula):
        self.op = op
        self.left = left
        self.right = right
        self.operator_string = ""

    def __repr__(self) -> str:
        from formula_types.ClassicalLogicFormula import Prop, Falsum, Verum
        from formula_types.HybridFormula import Nom

        string = ""
        if type(self.left) == Prop or type(self.left) == Nom or type(self.left) == Verum or type(self.left) == Falsum:
            string = string + f"{self.left}"
        else:
            string = string + f"({self.left})"

        string = string + f" {self.operator_string} "

        if type(self.right) == Prop or type(self.right) == Nom or type(self.right) == Verum or type(
                self.right) == Falsum:
            string = string + f"{self.right}"
        else:
            string = string + f"({self.right})"

        return string
