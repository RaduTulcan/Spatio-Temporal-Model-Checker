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

            if type(self.operand) == Next or type(self.operand) == Eventually or type(self.operand) == Always or type(self.operand) == Until:
                return self.operand.evaluate(new_trace, point)
            else:
                return self.operand.evaluate(new_trace[0], point)


class Eventually(UnaryOperator):
    """
        Class for temporal eventually operator.
    """

    def evaluate(self, trace, point):
        for i in range(0, len(trace)):
            if type(self.operand) == Next or type(self.operand) == Eventually or type(self.operand) == Always or type(self.operand) == Until:
                evaluation = self.operand.evaluate(trace[i:], point)
            else:
                evaluation = self.operand.evaluate(trace[i], point)

            if evaluation:
                return True

        return False



class Always(UnaryOperator):
    """
        Class for temporal always operator.
    """

    def evaluate(self, trace, point):
        for i in range(0, len(trace)):
            if type(self.operand) == Next or type(self.operand) == Eventually or type(self.operand) == Always or type(
                    self.operand) == Until:
                evaluation = self.operand.evaluate(trace[i:], point)
            else:
                evaluation = self.operand.evaluate(trace[i], point)

            if not evaluation:
                return False

        return True


class Until(BinaryOperator):
    """
        Class for temporal until operator.
    """
    pass
