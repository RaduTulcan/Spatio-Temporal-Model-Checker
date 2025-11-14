from itertools import chain, combinations, product

import HybridSpatioTemporalFormula
from baseline_version.parsers_baseline.HybridSpatioTemporalFormulaParser import tokenize, HybridSpatioTemporalParser
import copy


def powerset(iterable: iter) -> iter:
    """
    Returns the powerset of an iterable object.

    :param iterable: the iterable object
    :return: the powerset of the iterable object
    """
    s: list = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def generate_trace_from_spec(trace_spec: list[list[str]], grid_size: tuple[int, int]) -> list[list[list[list]]]:
    """
    Generates the trace data structure from the given trace model.

    :param trace_spec: the trace specification
    :param grid_size: the grid size used for the trace specification
    :return: the trace data structure used in the baseline algorithms
    """

    empty_grid: list[list[list]] = [[[] for _ in range(0, grid_size[1])] for _ in range(0, grid_size[0])]
    trace_length: int = len(trace_spec[0][0].split(";"))
    trace: list[list[list[list]]] = [copy.deepcopy(empty_grid) for _ in range(0, trace_length)]

    # fills the empty trace according to the trace specification
    for i in range(0, grid_size[0]):
        for j in range(0, grid_size[1]):
            point_time_evolution: list = trace_spec[i][j].split(";")

            for k in range(0, trace_length):
                if point_time_evolution[k] == "":
                    trace[k][i][j] = []
                else:
                    trace[k][i][j] = point_time_evolution[k].split(",")
    return trace


def generate_traces(propositions: list[str], nominals: list[str], max_trace_length: int, grid_size: tuple[int, int]) -> list[list[list[list]]]:
    """
    Generates all traces up to a given length based on the given grid structure.

    :param propositions: the set of propositions to be placed in the trace grids
    :param nominals: the set of nominals to be placed in the trace grids
    :param max_trace_length: the maximal length the traces should be
    :param grid_size: the dimensions of the grid the traces are build on
    :return: a finite trace of spatial grids
    """

    # generate all points found in the bounding box
    points:list[tuple[int,int]] = [(i, j) for i in range(grid_size[0]) for j in range(grid_size[1])]

    # generate all possible placements for each proposition
    prop_placements: list[list] = [list(powerset(points)) for _ in propositions]

    # generate all possible placements for each nominal
    nominal_placements: list[list[tuple[int, int]]] = [points for _ in nominals]

    empty_grid: list[list[list]] = [[[] for _ in range(0, grid_size[1])] for _ in range(0, grid_size[0])]
    grids: list[list[list[list]]] = []

    # iterate over all possible placements of atomic components
    for prop_choice in product(*prop_placements):
        for nominal_choice in product(*nominal_placements):
            placement: list[list[list]] = copy.deepcopy(empty_grid)

            # Add propositions with their chosen subsets
            for name, subset in zip(propositions, prop_choice):
                for s in subset:
                    placement[s[0]][s[1]].append(name)

            # Add nominals with their single chosen point
            for name, pos in zip(nominals, nominal_choice):
                placement[pos[0]][pos[1]].append(name)

            grids.append(placement)

    print("Total amount of grids generated:", len(grids))

    # generate all traces with the available grids and up to the given length
    for length in range(1, max_trace_length + 1):
        for tup in product(grids, repeat=length):
            yield list(tup)


def satisfying_points(formula: HybridSpatioTemporalFormula, trace: list[list[list[list]]], grid_size: tuple[int, int]):
    """
    Returns the spatial points in the grid where the given formula is true with respect to the given trace.

    :param formula: the formula to evaluate
    :param trace: the trace to evaluate the given formula on
    :param grid_size: the size of the spatial grids the trace has been defined on
    :return: the set of spatial points in the grid where the formula holds given the trace
    """
    points: list[tuple[int, int]] = []

    for i in range(0, grid_size[0]):
        for j in range(0, grid_size[1]):
            if formula.evaluate(trace, (i, j)):
                points.append((i, j))

    return points


def satisfying_trace_points(propositions: list[str], nominals: list[str], formula: HybridSpatioTemporalFormula, grid_size: tuple[int, int], max_trace_length: int, show_traces: bool):
    """
    Prints the number of traces and, if parameter show_traces, also the traces where spatial points have
    been found in which the given formula holds.

    :param propositions: the set of propositions used in the formula
    :param nominals: the set of nominals used in the formula
    :param formula: the formula to evaluate on generated traces
    :param grid_size: the dimensions of the grid the traces are build on
    :param max_trace_length: the maximal length the traces should be
    :param show_traces: whether the satisfying traces should be shown in the console
    """

    counter = 1

    # evaluate the input formula on all the generated traces over the given propositions
    # and nominals, and with maximal length max_trace_length
    for t in generate_traces(propositions, nominals, max_trace_length, grid_size):
        sat_points = satisfying_points(formula, t, grid_size)

        if sat_points:
            if show_traces:
                print("Satisfying trace #", counter, " with satisfying points: ", sat_points)
                print("--------------------------------------------------------------------")
                print(t, "\n")
            counter = counter + 1

    print("A total of ", counter, " satisfying traces found.")


if __name__ == '__main__':

    # list of propositions
    propositions = []

    # list of nominals
    nominals = ["z", "z2"]

    # list of assumptions (restrict the traces and points of interest)
    assumptions: list[str] = []

    # list of conclusions (formulas to be checked at all traces and spatial
    # points in which the assumptions hold)
    conclusions: list[str] = ["↓z F(z & z2)"]

    # size of the spatial grid graph (n x m)
    grid_size: tuple[int, int] = (3, 3)

    # specification spatio-temporal trace
    # indexes of the matrix represent indexes for the spatial points
    # the strings at (i,j) represent the temporal evolution of that
    # spatial point
    #
    # Example:
    # [                                     [                   [
    #  ["a;b" ";"],   represents the trace    ["a" ""], ----->    ["b" ""],
    #  ["b;"  ";"]                            ["b" ""]            [""  ""]
    # ]                                     ]                   ]
    trace_spec: list[list[str]] = [
        [";;", "z,b;z;a,z", ";;"],
        [";;", ";a;b", ";;"],
        [";;", "a;b;", "b;;"]
    ]

    # transform the input grid format into a trace
    trace: list[list[list[list]]] = generate_trace_from_spec(trace_spec, grid_size)

    # -------------------------------------------------------------------------
    # 1. EVALUATE FORMULA FOR GIVEN POINT AND TRACE
    # -------------------------------------------------------------------------

    # spatial point in the grid
    point: tuple[int, int] = (2, 1)

    # conjunction of assumptions and conclusion
    input_formula_string: str = "&".join([*("(" + x + ")" for x in conclusions), *("(" + x + ")" for x in assumptions)])

    # parse the input formula
    parsed_formula: HybridSpatioTemporalFormula = HybridSpatioTemporalParser(tokenize(input_formula_string)).parse()

    # evaluate formula w.r.t. trace and point
    print("EVALUATION WITH RESPECT TO GIVEN TRACE AND POINT")
    print("------------------------------------------------")
    print("The formula ", parsed_formula, " evaluates to ", parsed_formula.evaluate(trace, point), " at point ", point, "\n")

    # ---------------------------------------------------------------------------
    # 2. RETRIEVE POINTS FROM THE GRID WHERE THE FORMULA HOLDS FOR A GIVEN TRACE
    # ---------------------------------------------------------------------------

    print("EVALUATION WITH RESPECT TO GIVEN TRACE")
    print("------------------------------------------------")
    print("The formula ", parsed_formula, " is true at the following spatial points w.r.t. the given trace:", satisfying_points(parsed_formula, trace, grid_size), '\n')

    # ---------------------------------------------------------------------------
    # 3. RETRIEVE POINTS FROM THE GRID WHERE THE FORMULA HOLDS FOR A GIVEN TRACE
    # ---------------------------------------------------------------------------

    print("EVALUATION WITH RESPECT TO GRID SIZE")
    print("------------------------------------------------")
    satisfying_trace_points(propositions, nominals, parsed_formula, grid_size, 2, True)