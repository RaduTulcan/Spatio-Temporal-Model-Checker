from formula_types.UnaryFormula import UnaryFormula
from formula_types.HybridSpatioTemporalFormula import memoize


class Front(UnaryFormula):
    """
       Class for spatial front operator.
    """
    
    @memoize
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        if 0 <= point[0] - 1 < grid_size[0] and 0 <= point[1] < grid_size[1]:
            return self.operand.evaluate_memoized(trace, time, (point[0] - 1, point[1]), grid_size, memo)
        else: return False

class Back(UnaryFormula):
    """
        Class for spatial back operator.
    """
    @memoize
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        if 0 <= point[0] + 1 < grid_size[0] and 0 <= point[1] < grid_size[1]:
            return self.operand.evaluate_memoized(trace, time, (point[0] + 1, point[1]), grid_size, memo)
        else: return False 

class Left(UnaryFormula):
    """
        Class for spatial left operator.
    """
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        if 0 <= point[0]  < grid_size[0] and 0 <= point[1] - 1 < grid_size[1]:
            return self.operand.evaluate_memoized(trace, time, (point[0], point[1] - 1), grid_size, memo)
        else: return False

class Right(UnaryFormula):
    """
        Class for spatial right operator.
    """
    def evaluate_memoized(self, trace,time, point, grid_size, memo : dict[tuple[tuple, int, tuple[int, int]], bool]):
        if 0 <= point[0]  < grid_size[0] and 0 <= point[1] + 1 < grid_size[1]:
            return self.operand.evaluate_memoized(trace, time, (point[0], point[1] + 1), grid_size, memo)
        else: return False
