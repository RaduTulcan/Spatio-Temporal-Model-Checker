from checkers.SpatioTemporalEvaluatorUtils import satisfying_points, powerset
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from itertools import product
from parsers.HybridSpatioTemporalFormulaParser import HybridSpatioTemporalParser, tokenize


def generate_all_satisfying_grids(props: list[str], noms: list[str], grid_size: tuple[int, int],
                                  state_formulas: list[HybridSpatioTemporalFormula]) -> list[dict]:
    """
    This function generate all possible starting states in the grid. Since any position can be a starting point for any car, it generates all possible placements.

    :param props: propositions the formulas contain
    :param noms: nominals the formulas contain
    :param grid_size: size of the spatial grid
    :param state_formulas: set of state formulas
    :return: list of grid that satisfy state formulas
    """

    # generate all points found in the bounding box
    points: list[tuple[int, int]] = [(i, j) for i in range(grid_size[0]) for j in
                                     range(grid_size[1])]

    # generate all possible placements for each proposition
    prop_placements: list[list] = [list(powerset(points)) for _ in props]

    # generate all possible placements for each nominal
    nominal_placements: list[list[tuple[int, int]]] = [points for _ in noms]

    allowed_grids: list[dict] = []

    # iterate over all possible placements of atomic components
    for prop_choice in product(*prop_placements):
        for nominal_choice in product(*nominal_placements):
            placement: dict = {}

            # Add propositions with their chosen subsets
            for name, subset in zip(props, prop_choice):
                placement[name] = list(subset)

            # Add nominals with their single chosen point (wrapped in a list)
            for name, pos in zip(noms, nominal_choice):
                placement[name] = pos

            # check whether in the generated state, the assumptions hold
            formulas_hold: bool = True
            for fml in state_formulas:
                for p in points:
                    if not fml.evaluate([placement], p, grid_size):
                        formulas_hold = False
                        break

                if not formulas_hold:
                    break

            # consider these states, only if the assumption holds
            if formulas_hold:
                allowed_grids.append(placement)
            else:
                pass
    return allowed_grids


def generate_traces(props: list[str], noms: list[str], max_trace_length: int, grid_size: tuple[int, int],
                    parsed_state_formulas: list[HybridSpatioTemporalFormula]) -> list[list[dict]]:
    """
    Generates all traces up to a given length based on the given grid structure.

    :param props: propositions the formulas contain
    :param noms: nominals the formulas contain
    :param grid_size: size of the spatial grid
    :param max_trace_length: maximal length of traces
    :param parsed_state_formulas: set of state formula
    :return:
    """
    # consider only grids that satisfy state assumptions
    grids: list[dict] = generate_all_satisfying_grids(props, noms, grid_size, parsed_state_formulas)

    print("|Total amount of grids generated:", len(grids))

    # generate all traces with the available grids and up to the given length
    for length in range(1, max_trace_length + 1):
        for tup in product(grids, repeat=length):
            yield list(tup)


# She who fixes soundness bugs the afternoon of the deadline be not bound by style guides
def is_state_formula_string(s: str):
    toks = [x for x in tokenize(s) if x[1] != "(" and x[1] != ")"]
    if "X" in s or "U" in s or "F" in s:
        return False
    if len(toks) < 2:
        return False
    if toks[0][1] == 'G':
        if toks[1][1][0] == '@':
            return True
    return False


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
    """

    # filter global formula with propositional/hybrid or other global arguments
    state_fmls = []

    for a in assumptions + conclusions:
        if is_state_formula_string(a):
            state_fmls.append(a)

    parsed_state_fmls: list[HybridSpatioTemporalFormula] = [HybridSpatioTemporalParser(tokenize(assumption)).parse() for
                                                            assumption in
                                                            state_fmls]

    # conjunction of assumptions and conclusion
    input_formula_string: str = "&".join([*("(" + x + ")" for x in conclusions),
                                          *("(" + x + ")" for x in set(assumptions).difference(state_fmls))])

    # parse the input formula
    parsed_formula: HybridSpatioTemporalFormula = HybridSpatioTemporalParser(tokenize(input_formula_string)).parse()

    counter_sat: int = 0
    counter_gen: int = 0

    # evaluate the input formula on all the generated traces over the given propositions
    # and nominals, and with maximal length max_trace_length
    for t in generate_traces(props, noms, max_trace_length, grid_size, parsed_state_fmls):
        sat_points = satisfying_points(parsed_formula, t, grid_size)

        if sat_points:
            if show_traces:
                print("\t |Satisfying trace #", counter_sat, " with satisfying points: ", sat_points)
                print("\t |--------------------------------------------------------------------")
                print("\t |", t, "\n")
            counter_sat = counter_sat + 1
        counter_gen = counter_gen + 1

    print("|A total of ", counter_gen, "traces generated.")
    print("|A total of ", counter_sat, " satisfying traces found.")
