from formula_types.UnaryOperator import UnaryOperator
from formula_types.BinaryOperator import BinaryOperator


class Next(UnaryOperator):
    """
        Class for temporal next operator.
    """
    def evaluate(self, trace, point):
        if len(trace) == 1:
            return False
        else:
            new_trace = trace[1:]
            return self.operand.evaluate(new_trace, point)


class Eventually(UnaryOperator):
    """
        Class for temporal eventually operator.
    """

    def evaluate(self, trace, point):
        for i in range(0, len(trace)):
            evaluation = self.operand.evaluate(trace[i:], point)

            if evaluation:
                return True

        return False



class Always(UnaryOperator):
    """
        Class for temporal always operator.
    """

    def evaluate(self, trace, point):
        for i in range(0, len(trace)):
            evaluation = self.operand.evaluate(trace[i:], point)

            if not evaluation:
                return False

        return True


class Until(BinaryOperator):
    """
        Class for temporal until operator.
    """
    def evaluate(self, trace, point):
        for i in range(0, len(trace)):
            if i == 0 and self.right.evaluate(trace[i:], point):
                return True

            if not self.right.evaluate(trace[i:], point):
                continue
            else:
                for j in range(0, i):
                    if not self.left.evaluate(trace[j:], point):
                        return False
                return True

        return False