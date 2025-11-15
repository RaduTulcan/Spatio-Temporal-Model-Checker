from HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from baseline_version.evaluator_baseline.SpatioTemporalEvaluator import satisfying_trace_points
from baseline_version.parsers_baseline.HybridSpatioTemporalFormulaParser import tokenize, HybridSpatioTemporalParser
from timeit import default_timer as timer


def run_evaluator(run_id: int, propositions: list[str], nominals: list[str], assumptions: list[str], conclusions: list[str], grid_size: tuple[int, int], trace_max_length: int, show_traces: bool):
    """
    Returns for a given formula all (trace, points) tuples where the formula holds.

    :param run_id: the id of the run
    :param propositions: the list of propositions used in the formula
    :param nominals: the list of nominals used in the formula
    :param assumptions: the list of formulas used as assumptions
    :param conclusions: the list of formulas used as conclusions
    :param grid_size: the grid size used for building the traces
    :param trace_max_length: the maximal length of traces to consider
    :param show_traces: whether the (trace, point) tuples should be displayed in the console
    """

    # conjunction of assumptions and conclusion
    input_formula_string: str = "&".join([*("(" + x + ")" for x in conclusions), *("(" + x + ")" for x in assumptions)])

    # parse the input formula
    parsed_formula: HybridSpatioTemporalFormula = HybridSpatioTemporalParser(tokenize(input_formula_string)).parse()

    print("| Run ", run_id, " started")
    print("|--------------------")
    print("|Number of propositions:", len(propositions))
    print("|Number of nominals:", len(nominals))
    print("|Formula to check:", parsed_formula)
    print("|Grid size:", grid_size)
    print("|Maximal trace length:", trace_max_length)

    # evaluate formula and return traces and points where the formula holds
    start: float = timer()
    satisfying_trace_points(propositions, nominals, parsed_formula, grid_size, trace_max_length, show_traces)
    end: float = timer()

    print("|Time elapsed:", end - start, "\n")


if __name__ == '__main__':
    # Test 1
    run_evaluator(1, [], ['z'], [], ["Front(Back(z)) <-> Back(Front(z))"], (3,3), 3, False)

    # Test 2
    run_evaluator(2, [], ['z', 'z1'], [], ["G (@z z1)"], (3, 3), 3, False)