from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula


class UnaryFormula(HybridSpatioTemporalFormula):
    """
    Class for unary formulas.
    """

    def __init__(self, op: str, operand: HybridSpatioTemporalFormula):
        self.op = op
        self.operand = operand
        self.operator_string = ""


    def __repr__(self) -> str:
        from formula_types.ClassicalLogicFormula import Prop, Falsum, Verum
        from formula_types.HybridFormula import Nom

        if type(self.operand) == Prop or type(self.operand) == Nom or type(self.operand) == Verum or type(self.operand) == Falsum:
            return f"{self.operator_string} {self.operand}"
        else:
            return f"{self.operator_string}({self.operand})"