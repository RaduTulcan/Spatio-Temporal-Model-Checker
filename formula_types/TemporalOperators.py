from formula_types.UnaryOperator import UnaryOperator
from formula_types.BinaryOperator import BinaryOperator


class Next(UnaryOperator):
    """
        Class for temporal next operator.
    """
    pass


class Eventually(UnaryOperator):
    """
        Class for temporal eventually operator.
    """
    pass


class Always(UnaryOperator):
    """
        Class for temporal always operator.
    """
    pass


class Until(BinaryOperator):
    """
        Class for temporal until operator.
    """
    pass
