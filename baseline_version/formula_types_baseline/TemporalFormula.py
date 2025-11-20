from BinaryFormula import BinaryFormula
from UnaryFormula import UnaryFormula


class Next(UnaryFormula):
    """
        Class for temporal next operator.
    """
    def evaluate(self, trace, point):
        if len(trace) == 1:
            return False
        else:
            new_trace = trace[1:]
            return self.operand.evaluate(new_trace, point)


class Eventually(UnaryFormula):
    """
        Class for temporal eventually operator.
    """

    def evaluate(self, trace, point):
        for i in range(0, len(trace)):

            if self.operand.evaluate(trace[i:], point):
                return True

        return False



class Always(UnaryFormula):
    """
        Class for temporal always operator.
    """

    def evaluate(self, trace: list[list[list[list]]], point: tuple[int, int]) -> bool:
        for i in range(0, len(trace)):

            if not self.operand.evaluate(trace[i:], point):
                return False

        return True


class Until(BinaryFormula):
    """
        Class for temporal until operator.
    """
    def evaluate(self, trace: list[list[list[list]]], point: tuple[int, int]) -> bool:
        for i in range(0, len(trace)):
            eval_right = self.right.evaluate(trace[i:], point)
            if eval_right:
                return True
            
            elif not self.left.evaluate(trace[i:], point):
                return False
            
        return False
