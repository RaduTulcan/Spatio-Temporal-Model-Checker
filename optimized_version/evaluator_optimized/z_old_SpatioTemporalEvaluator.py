from HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from optimized_version.parsers_optimized.HybridSpatioTemporalFormulaParser import HybridSpatioTemporalParser, tokenize
from itertools import chain, combinations, product


def powerset(iterable: iter) -> iter:
    """
    Returns the powerset of an iterable object.

    :param iterable: the iterable object
    :return: the powerset of the iterable object
    """
    s: list = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def generate_all_satisfying_grids(size_of_bounding_box, propositions, nominals, assumptions):
    """
        This function generate all possible starting states in the grid.
        (Since any position can be a starting point for any car, it generates all possible placements)
    """

    # generate all points found in the bounding box
    points: list[tuple[int, int]] = [(i, j) for i in range(size_of_bounding_box[0]) for j in range(size_of_bounding_box[1])]

    # generate all possible placements for each proposition
    prop_placements: list[list] = [list(powerset(points)) for _ in propositions]

    # generate all possible placements for each nominal
    nominal_placements: list[list[tuple[int, int]]] = [points for _ in nominals]

    allowed_grids: list[dict] = []

    # iterate over all possible placements of atomic components
    for prop_choice in product(*prop_placements):
        for nominal_choice in product(*nominal_placements):
            placement: dict = {}

            # Add propositions with their chosen subsets
            for name, subset in zip(propositions, prop_choice):
                placement[name] = list(subset)

            # Add nominals with their single chosen point (wrapped in a list)
            for name, pos in zip(nominals, nominal_choice):
                placement[name] = pos

            # check whether in the generated state, the assumptions hold
            assumptions_hold: bool = True
            for assumption in assumptions:
                for p in points:
                    if not assumption.evaluate([placement], p):
                        assumptions_hold = False
                        break

                if not assumptions_hold:
                    break

            # consider these states, only if the assumption holds
            if assumptions_hold:
                allowed_grids.append(placement)
    return allowed_grids

def generate_traces(propositions: list[str], nominals: list[str], max_trace_length: int, grid_size: tuple[int, int], parsed_state_assumptions) -> list[list[list[list]]]:
    """
    Generates all traces up to a given length based on the given grid structure.

    :param propositions: the set of propositions to be placed in the trace grids
    :param nominals: the set of nominals to be placed in the trace grids
    :param max_trace_length: the maximal length the traces should be
    :param grid_size: the dimensions of the grid the traces are build on
    :return: a finite trace of spatial grids
    """

    # consider only grids that satisfy state assumptions
    grids: list[dict] = generate_all_satisfying_grids(grid_size, propositions, nominals, parsed_state_assumptions)

    print("|Total amount of grids generated:", len(grids))

    nr_traces: int = 0

    for i in range(1, max_trace_length + 1):
        nr_traces += len(grids)**i

    print("|Total amount of traces to check:", nr_traces)

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

def satisfying_trace_points(propositions: list[str], nominals: list[str], formula: HybridSpatioTemporalFormula, parsed_state_assumptions, grid_size: tuple[int, int], max_trace_length: int, show_traces: bool):
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

    counter = 0

    # evaluate the input formula on all the generated traces over the given propositions
    # and nominals, and with maximal length max_trace_length
    for t in generate_traces(propositions, nominals, max_trace_length, grid_size, parsed_state_assumptions):
        sat_points = satisfying_points(formula, t, grid_size)

        if sat_points:
            if show_traces:
                print("\t |Satisfying trace #", counter, " with satisfying points: ", sat_points)
                print("\t |--------------------------------------------------------------------")
                print("\t |", t, "\n")
            counter = counter + 1

    print("|A total of ", counter, " satisfying traces found.")


if __name__ == '__main__':

    # list of propositions
    propositions = []

    # list of nominals
    nominals = ["z", "z2"]

    # list of assumptions (restrict the traces and points of interest)
    assumptions: list[str] = ["G(! @z z2)"]

    # list of conclusions (formulas to be checked at all traces and spatial
    # points in which the assumptions hold)
    conclusions: list[str] = ["↓z F(z & z2)"]

    # size of the spatial grid graph (n x m)
    grid_size: tuple[int, int] = (3, 3)

    # -----------------------------------------------------------------------------
    # 3. RETRIEVE POINTS FROM THE GRID WHERE THE FORMULA HOLDS FOR ARBITRARY TRACES
    # -----------------------------------------------------------------------------

    print("EVALUATION WITH RESPECT TO GRID SIZE")
    print("------------------------------------------------")

    # only allow assumptions that are either purely classical and hybrid, and contains only operator G with argument
    # a purely classical or hybrid formula
    state_assumptions = []

    for a in assumptions:
        if "X" not in a and "U" not in a and "F" not in a:
            state_assumptions.append(a)

    parsed_state_assumptions = [HybridSpatioTemporalParser(tokenize(assumption)).parse() for assumption in state_assumptions]

    # conjunction of assumptions and conclusion
    input_formula_string: str = "&".join([*("(" + x + ")" for x in conclusions), *("(" + x + ")" for x in set(assumptions).difference(state_assumptions))])

    # parse the input formula
    parsed_formula: HybridSpatioTemporalFormula = HybridSpatioTemporalParser(tokenize(input_formula_string)).parse()

    # compute the satisfying trace-point pairs
    satisfying_trace_points(propositions, nominals, parsed_formula, parsed_state_assumptions, grid_size, 2, True)




