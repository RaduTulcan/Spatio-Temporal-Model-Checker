class HybridSpatioTemporalFormula:
    def evaluate(self, trace: list[dict], point: tuple[int, int], grid_size: tuple[int, int]) -> bool:
        """
        Evaluates the formula on the given trace at the specified point starting from time 0.

        :param trace: trace the formula is evaluated on
        :param point: spatial point the formula is evaluated on
        :param grid_size: size of the spatial grid
        :return: true if the formula is satisfied w.r.t. the given point and trace
        """
        return self.evaluate_memoized(trace, 0, point, grid_size, {})

    def evaluate_memoized(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                          memo: dict[tuple['HybridSpatioTemporalFormula', int], bool]) -> bool:
        """
        Evaluates the formula on the given trace, at the specified point and time, using memoized strategy.

        :param trace: trace the formula is evaluated on
        :param time: time instance
        :param point: spatial point the formula is evaluated on
        :param grid_size:size of the spatial grid
        :param memo: dictionary for memoized evaluation strategy
        :return: true if the formula is satisfied w.r.t. the given point and trace (starting at the specified time instance)
        """
        raise NotImplementedError("Subclasses should implement this method.")


def memoize(method):
    """
        Decorator to memoize evaluation results of HybridSpatioTemporalFormula methods.
        Caches results based on the formula instance, time, and spatial point.
    """

    def wrapper(self, trace: list[dict], time: int, point: tuple[int, int], grid_size: tuple[int, int],
                memo: dict[tuple['HybridSpatioTemporalFormula', int], bool]) -> bool:
        key: tuple[HybridSpatioTemporalFormula, int] = (self, time)
        if key in memo:
            return memo[key]
        result: bool = method(self, trace, time, point, grid_size, memo)
        memo[key] = result
        return result

    return wrapper
