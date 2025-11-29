from itertools import chain, combinations
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula


def powerset(iterable: iter) -> iter:
    """
    Returns the powerset of an iterable object.

    :param iterable: the iterable object
    :return: the powerset of the iterable object
    """
    s: list = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def generate_trace_from_spec(spec: list[list[str]], grid_size: tuple[int, int]) -> list[dict]:
    """
    Generates the trace data structure from the given trace model.

    :param spec: the trace specification
    :param grid_size: the grid size used for the trace specification
    :return: the trace data structure used in the baseline algorithms
    """

    trace_length: int = len(spec[0][0].split(";"))
    trace: list[dict] = [{} for _ in range(0, trace_length)]

    # fill the empty trace according to the trace specification
    for i in range(0, grid_size[0]):
        for j in range(0, grid_size[1]):
            point_time_evolution: list = spec[i][j].split(";")

            for k in range(0, trace_length):
                for s in point_time_evolution[k].split(","):
                    if s == "":
                        continue

                    # assign positions to propositions and nominals
                    if s.startswith("z"):
                        trace[k][s] = (i, j)
                    elif "a" <= s[0].lower() <= "y":
                        if s not in trace[k]:
                            trace[k][s] = [(i, j)]
                        else:
                            trace[k][s].append((i, j))
    return trace


def satisfying_points(formula: HybridSpatioTemporalFormula, eval_trace: list[dict], grid_size: tuple[int, int]) -> list[
    tuple[int, int]]:
    """
    Returns the spatial points in the grid where the given formula is true with respect to the given trace.

    :param formula: the formula to evaluate
    :param eval_trace: the trace to evaluate the given formula on
    :param grid_size: the size of the spatial grids the trace has been defined on
    :return: the set of spatial points in the grid where the formula holds given the trace
    """

    points: list[tuple[int, int]] = []

    for i in range(0, grid_size[0]):
        for j in range(0, grid_size[1]):
            if formula.evaluate(eval_trace, (i, j), grid_size):
                points.append((i, j))

    return points
