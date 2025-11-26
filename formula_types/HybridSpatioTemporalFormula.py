class HybridSpatioTemporalFormula:
    pass

def memoize(method):
    def wrapper(self, trace, time, point, memo):
        key = (self, time, point)
        if key in memo:
            return memo[key]
        result = method(self, trace, time, point, memo)
        memo[key] = result
        return result
    return wrapper
