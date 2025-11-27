class HybridSpatioTemporalFormula:
    def evaluate(self, trace, point, grid_size):
        """
            Evaluates the formula on the given trace at the specified point starting from time 0.
        """
        return self.evaluate_memoized(trace, 0, point, grid_size, {})
    
    def evaluate_memoized(self, trace, time, point, grid_size, memo : dict[tuple['HybridSpatioTemporalFormula', int, tuple[int, int]], bool]):
        raise NotImplementedError("Subclasses should implement this method.")

def memoize(method):
    """
        Decorator to memoize evaluation results of HybridSpatioTemporalFormula methods.
        Caches results based on the formula instance, time, and spatial point.
    """
    def wrapper(self, trace, time, point, grid_size, memo):
        key = (self, time)
        if key in memo:
            return memo[key]
        result = method(self, trace, time, point, grid_size, memo)
        memo[key] = result
        return result
    return wrapper
