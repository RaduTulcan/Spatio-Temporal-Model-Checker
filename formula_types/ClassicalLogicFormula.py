from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula, memoize
from formula_types.UnaryFormula import UnaryFormula
from formula_types.BinaryFormula import BinaryFormula


class Verum(HybridSpatioTemporalFormula):
    """
        Class for logical constant "true".
    """
    def __repr__(self):
        return "⊤"

    @memoize
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[HybridSpatioTemporalFormula, int, tuple[int, int]], bool]):
        return True


class Falsum(HybridSpatioTemporalFormula):
    """
        Class for logical constant "false".
    """
    def __repr__(self):
        return "⊥"

    @memoize
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[HybridSpatioTemporalFormula, int, tuple[int, int]], bool]):
        return False


class Prop(HybridSpatioTemporalFormula):
    """
       Class for logical propositions.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    @memoize
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[HybridSpatioTemporalFormula, int, tuple[int, int]], bool]):
        return point in trace[time][self.name]



# --------------------------------------------------------------------------
# 1-ary operators
# --------------------------------------------------------------------------
class Not(UnaryFormula):
    """
       Class for logical negation.
    """

    @memoize
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[HybridSpatioTemporalFormula, int, tuple[int, int]], bool]):
        return not self.operand.evaluate_memoized(trace, time, point, grid_size, memo)


# --------------------------------------------------------------------------
# 2-ary operators
# --------------------------------------------------------------------------


class And(BinaryFormula):
    """
       Class for logical constant conjunction.
    """
    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

    @memoize
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[HybridSpatioTemporalFormula, int, tuple[int, int]], bool]):
        return self.left.evaluate_memoized(trace, time, point, grid_size, memo) and self.right.evaluate_memoized(trace, time, point, grid_size, memo)


class If(BinaryFormula):
    """
       Class for logical implication.
    """
    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

    @memoize
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[HybridSpatioTemporalFormula, int, tuple[int, int]], bool]):
        return (not self.left.evaluate_memoized(trace, time, point, grid_size, memo)) or self.right.evaluate_memoized(trace, time, point, grid_size, memo)


class Iff(BinaryFormula):
    """
       Class for logical bi-implication.
    """
    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

    @memoize
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[HybridSpatioTemporalFormula, int, tuple[int, int]], bool]):
        return ((not self.left.evaluate_memoized(trace, time, point, grid_size, memo)) or self.right.evaluate_memoized(trace, time, point, grid_size, memo)) and (
                (not self.right.evaluate_memoized(trace, time, point, grid_size, memo)) or self.left.evaluate_memoized(trace, time, point, grid_size, memo))


class Or(BinaryFormula):
    """
       Class for logical disjunction.
    """
    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"
    
    @memoize
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[HybridSpatioTemporalFormula, int, tuple[int, int]], bool]):
        return self.left.evaluate_memoized(trace, time, point, grid_size, memo) or self.right.evaluate_memoized(trace, time, point, grid_size, memo)

