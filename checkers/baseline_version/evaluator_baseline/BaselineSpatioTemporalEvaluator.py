from itertools import product
from checkers.SpatioTemporalEvaluatorUtils import powerset, satisfying_points
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from parsers.HybridSpatioTemporalFormulaParser import tokenize, HybridSpatioTemporalParser


def generate_traces(props: list[str], noms: list[str], max_trace_length: int, grid_size: tuple[int, int]) -> list[
    list[dict]]:
    """
    Generates all traces up to a given length based on the given grid structure.

    :param props: the set of propositions to be placed in the trace grids
    :param noms: the set of nominals to be placed in the trace grids
    :param max_trace_length: the maximal length the traces should be
    :param grid_size: the dimensions of the grid the traces are build on
    :return: a finite trace of spatial grids
    """

    # generate all points found in the bounding box
    points: list[tuple[int, int]] = [(i, j) for i in range(grid_size[0]) for j in range(grid_size[1])]

    # generate all possible placements for each proposition
    prop_placements: list[list] = [list(powerset(points)) for _ in props]

    # generate all possible placements for each nominal
    nominal_placements: list[list[tuple[int, int]]] = [points for _ in noms]

    grids: list = []

    # iterate over all possible placements of atomic components
    for prop_choice in product(*prop_placements):
        for nominal_choice in product(*nominal_placements):
            placement: dict = {}

            # Add propositions with their chosen subsets
            for name, subset in zip(props, prop_choice):
                placement[name] = subset

            # Add nominals with their single chosen point
            for name, pos in zip(noms, nominal_choice):
                placement[name] = pos

            grids.append(placement)

    print("|Total amount of grids generated:", len(grids))

    # generate all traces with the available grids and up to the given length
    for length in range(1, max_trace_length + 1):
        for tup in product(grids, repeat=length):
            yield list(tup)


def evaluate(props, noms, assumptions, conclusions, grid_size, max_trace_length, show_traces):
    """
    Prints the number of traces and, if parameter show_traces, also the traces where spatial points have
    been found in which the given formula holds.

    :param props: the set of propositions used in the formula
    :param noms: the set of nominals used in the formula
    :param assumptions: list of assumptions that hold
    :param conclusions: list of conclusions to check
    :param grid_size: the dimensions of the grid the traces are build on
    :param max_trace_length: the maximal length the traces should be
    :param show_traces: whether the satisfying traces should be shown in the console
    :return: 
    """
    # conjunction of assumptions and conclusion
    input_formula_string: str = "&".join([*("(" + x + ")" for x in conclusions), *("(" + x + ")" for x in assumptions)])

    # parse the input formula
    parsed_formula: HybridSpatioTemporalFormula = HybridSpatioTemporalParser(tokenize(input_formula_string)).parse()

    counter_sat: int = 0
    counter_gen: int = 0

    # evaluate the input formula on all the generated traces over the given propositions
    # and nominals, and with maximal length max_trace_length
    for t in generate_traces(props, noms, max_trace_length, grid_size):
        sat_points: list[tuple[int, int]] = satisfying_points(parsed_formula, t, grid_size)

        if sat_points:
            if show_traces:
                print("\t |Satisfying trace #", counter_sat, " with satisfying points: ", sat_points)
                print("\t |--------------------------------------------------------------------")
                print("\t |", t, "\n")
            counter_sat = counter_sat + 1
        counter_gen = counter_gen + 1

    print("|A total of ", counter_gen, "traces generated.")
    print("|A total of ", counter_sat, " satisfying traces found.")
