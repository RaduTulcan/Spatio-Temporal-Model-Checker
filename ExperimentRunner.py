import multiprocessing
import sys
from functools import reduce
from pathlib import Path
from timeit import default_timer as timer
from typing import Callable

from checkers.baseline_version.evaluator_baseline.BaselineSpatioTemporalEvaluator import evaluate as evaluate_baseline
from checkers.optimized_version.evaluator_optimized.OptimizedSpatioTemporalEvaluator1 import \
    evaluate as evaluate_optimized1
from checkers.optimized_version.evaluator_optimized.OptimizedSpatioTemporalEvaluator2 import \
    evaluate as evaluate_optimized2
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from parsers.HybridSpatioTemporalFormulaParser import HybridSpatioTemporalParser, tokenize

import argparse


def evaluate_handler(propositions: list[str], nominals: list[str], assumptions: list[str], conclusions: list[str],
                     grid_size: tuple[int, int], trace_max_length: int, show_traces: bool, evaluate: Callable):
    """
    Runs the evaluation function of the model checker.

   :param propositions: the list of propositions used in the formula
   :param nominals: the list of nominals used in the formula
   :param assumptions: the list of formulas used as assumptions
   :param conclusions: the list of formulas used as conclusions
   :param grid_size: the grid size used for building the traces
   :param trace_max_length: the maximal length of traces to consider
   :param show_traces: whether the (trace, point) tuples should be displayed in the console
   :param evaluate: model checker evaluation function
   """
    start: float = timer()
    evaluate(propositions, nominals, assumptions, conclusions, grid_size, trace_max_length, show_traces)
    end: float = timer()
    print("|TimeX:", end - start, "\n")


def run_evaluator(run_id: int, propositions: list[str], nominals: list[str], assumptions: list[str],
                  conclusions: list[str], grid_size: tuple[int, int], trace_max_length: int, show_traces: bool,
                  evaluator_function: Callable):
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
   :param evaluator_function: model checker evaluation function
   """
    TIMEOUT = 600

    # conjunction of assumptions and conclusion
    input_formula_string: str = "&".join([*("(" + x + ")" for x in conclusions), *("(" + x + ")" for x in assumptions)])

    # parse the input formula
    parsed_formula: HybridSpatioTemporalFormula = HybridSpatioTemporalParser(tokenize(input_formula_string)).parse()

    print("| Test ", run_id, " started")
    print("|--------------------")
    print("|[Not in Table 1]Formula to check:", parsed_formula)
    print("|Noms:" + str(len(nominals))+",Grid:"+str(grid_size)+",Len:"+str(trace_max_length))
    
    # evaluate formula and return traces and points where the formula holds
    p = multiprocessing.Process(target=evaluate_handler, args=(
        propositions, nominals, assumptions, conclusions, grid_size, trace_max_length, show_traces, evaluator_function))
    p.start()
    p.join(TIMEOUT)
    if p.is_alive():
        print("=====================   TIMED OUT ===========================")
        p.terminate()
        p.join()


def left_right_test(test_index: int, evaluator_function: Callable):
    """
    Tests a spatial validity.

   :param test_index: test index
   :param evaluator_function: function of the checker for evaluating the formula
   """
    run_evaluator(test_index, [], ['z'], [], ["G(Left(Right(z)) <-> Right(Left(z)))"], (3, 3), 3, False,
                  evaluator_function)


def same_name_test(test_index: int, evaluator_function: Callable):
    """
    Tests a hybrid formula.

   :param test_index: test index
   :param evaluator_function: function of the checker for evaluating the formula
   :return:
   """
    run_evaluator(test_index, [], ['z', 'z1'], [], ["G (@z z1)"], (3, 3), 3, False, evaluator_function)


def one_lane_follow_test(test_index: int, duration: int, road_length: int, evaluator_function: Callable):
    """
    Test whether vehicle can safely follow another in the same lane.
    A detailed description can be found in README.md/Experiments/One Lane Follow.

    :param test_index: test index
    :param duration: maximal length of the traces
    :param road_length: length of the one-lane road
    :param evaluator_function: function of the checker for evaluating the formula
    """
    run_evaluator(test_index, [], ['z0', 'z1'],
                  ["@z0 !(Back 1)",  # SV is initially at the start of the lane
                   "G (@z1 ↓z2 ((! X 1) | X @z1  (z2 | Back z2)))",  # POV always moves forward or stays put
                   "G (@z0 ↓z2 ((! X 1) | X (@z0 ((!z1 & Back z2 ) | (z2 & Front z1) ))))"],
                  # SV Always moves forward if safe, stays put if POV immediately ahead
                  ["G(@z0 ! z1)"], (road_length, 1), duration, False, evaluator_function)


def hazard_test(test_index: int, duration: int, evaluator_function: Callable):
    """
    Tests whether vehicle can avoid static hazard in presence of another vehicle.
    Figure 3 in paper
    
    :param test_index: test index
    :param duration: maximal length of traces
    :param evaluator_function: function of the checker for evaluating the formula
    """
    width = 2
    length = 2

    def fronts(i: int, p: str):
        if i == 0:
            return "({})".format(p)
        else:
            return "(Front {})".format(fronts(i - 1, p))

    def bfront(p: str):
        each = ["(({})->({}))".format(fronts(i + 1, "1"), fronts(i + 1, p)) for i in range(0, length)]
        return "({})".format(reduce((lambda x, acc: x + "&" + acc), each))

    def dfront(p: str):
        each = [fronts(i + 1, p) for i in range(0, length)]
        return "({})".format(reduce((lambda x, acc: x + "|" + acc), each))

    p1 = "(Right z1) & {}".format(dfront("G h"))
    p2 = "(@z0 ↓z2 X @z0 ((Back z2) & (G ! h)))"
    p3 = "(@z0 ↓z2 X @z0((Left z2) & {} & {}))".format(dfront("z1"), bfront("G ! h"))
    full = "@z0 (({}) & (({}) U ({})))".format(p1, p2, p3)
    run_evaluator(test_index, ["h"], ["z0", "z1"], [], [full], (length, width), duration, False, evaluator_function)


def safe_intersection_priority(test_index: int, duration: int, grid_size: int, evaluator_function: Callable):
    """
    Test whether vehicle can go through an intersection safely.
    A detailed description can be found in README.md/Experiments/Safe Intersection with Priority.

    :param test_index: test index
    :param duration: maximal length of the traces
    :param road_length: width and length of the road
    :param evaluator_function: function of the checker for evaluating the formula
    """
    run_evaluator(test_index, [], ['z0', 'z1'],
                  ["@z1 !(Left 1)",  # z1 starts somewhere on the left border
                   "@z0 !(Back 1)",  # z0 starts somewhere on the bottom border
                   "G (@z1 ↓z2 ((! X 1)| X @z1 (Left z2)))",  # Moves left-to-right always
                   "G (@z0 ↓z2 ((! X 1)| X @z0 ((!z1 & Back z2) | (z2 & Front z1) )))"],
                  # Moves bottom-to-top except it stops to avoid other vehicle.
                  ["G (@z0 !z1)"], (grid_size, grid_size), duration, False, evaluator_function)


def safe_passing(test_index: int, duration: int, road_length: int, evaluator_function: Callable):
    """
    Tests maneuvers of vehicles: speed-up, swerving left and right.
     A detailed description can be found in README.md/Experiments/Safe Passing.

    :param test_index: test index
    :param duration: maximal length of the traces
    :param road_length: width and length of the road
    :param evaluator_function: function of the checker for evaluating the formula
    """
    # z0 initially moves forward
    first_forward = "(@z0 ↓z2 ((! X 1) | X @z0 (Back z2)))"
    # then swerves left to avoid z1
    dodge_left = "(@z0 ↓z2 ((Front z1) & ((! X 1)| X (@z0 (Back (Right z2))))))"
    # then drives twice as fast
    fast_forward = "(@z0 ↓z2 ((! X 1)| X @z0 (Back (Back z2))))"
    # then dodges back when safe
    dodge_right = "(@z0 ↓z2 ((! X 1)| X @z0 (Back (Left z2))))"
    # then drives normally
    last_forward = "(@z0 ↓z2 ((! X 1) | X @z0 (Back z2)))"
    run_evaluator(test_index, [], ['z0', 'z1'],
                  ["G(@z1 !(Right 1))",  # POV starts anywhere in right lane, stays in right lane
                   "@z0 !(Right 1)",  # SV starts in back of right lane
                   "@z0 !(Back 1)",
                   "G (@z1 ↓z2 ((! X 1) | X @z1  (z2 | Back z2)))",  # z1 moves forward or stays in place
                   "({} U ({} & ((! X 1) | X ({} & ((! X 1) | X ({} U ({} & ((! X 1) | X G ({})))))))))".format(
                       first_forward, dodge_left, fast_forward, fast_forward, dodge_right, last_forward)],
                  ["G (@z0 !z1)"], (road_length, 2), duration, False, evaluator_function)


def join_platoon(test_index: int, duration: int, platoon_size: int, road_length: int, evaluator_function: Callable):
    """
    Tests safe joining of a vehicle to a platoon of other vehicles.

    :param test_index: test index
    :param duration: maximal length of the traces
    :param platoon_size: size of vehicle platoon
    :param road_length: width and length of the road
    :param evaluator_function: function of the checker for evaluating the formula
    """
    pov_noms = ["z" + str(i + 1) for i in range(platoon_size)]
    noms = ["z0"] + pov_noms  # and z is a temporary
    no_collide = "!({})".format(reduce((lambda x, acc: x + "|" + acc), pov_noms))
    each_front = ["Front " + n for n in pov_noms]
    some_front = reduce((lambda x, acc: x + "|" + acc), each_front)
    sv_mov_assump = "G(@z0 ↓z ((! X 1) | (X @z0((Back z)|(({0})&(Right z)&({1}))))))".format(some_front, no_collide)
    sv_start_assump = "@z0 !(Right 1)"
    pov_start_assumps = [format("G(@z{0} !(Left 1))".format(str(i + 1))) for i in range(platoon_size)]
    pov_mov_assumps = [format("G(@z{0} ↓z ((! X 1) | X (@z{0} (Back z))))".format(str(i + 1))) for i in
                       range(platoon_size)]
    assumps = [sv_start_assump, sv_mov_assump] + pov_mov_assumps + pov_start_assumps
    postcond = "G(@z0 ({}))".format(no_collide)
    run_evaluator(test_index, [], noms, assumps, [postcond], (road_length, 2), duration, False, evaluator_function)


def global_soundness(test_index: int, duration: int, evaluator_function: Callable):
    run_evaluator(test_index, [], ["z0"], ["G !(Left 1)"], ["1"], (2, 2), duration, False, evaluator_function)


BAR_STR = "###########################################################"
EVALUATORS = [evaluate_baseline, evaluate_optimized1, evaluate_optimized2]
EVALUATOR_MSGS = ["Running BASELINE algorithm (columns TraceX=Trace1, TimeX=Time1)", "Running OPTIMIZED algorithm (columns TraceX=Trace2, TimeX=Time2)", "Running MOTION algorithm (columns TraceX=Trace3, TimeX=Time3)"]

def run_quick_test_cases():
    """
    Runs the set of fast test cases.
    """
    for msg, funct in zip(EVALUATOR_MSGS, EVALUATORS):
        print("", BAR_STR, "\n#", msg, "\n", BAR_STR)
        left_right_test(1, funct)
        same_name_test(2, funct)
        one_lane_follow_test(3, 3, 3, funct)
        one_lane_follow_test(4, 3, 6, funct)
        one_lane_follow_test(5, 3, 9, funct)
        one_lane_follow_test(6, 3, 12, funct)
        hazard_test(9, 2, funct)
        hazard_test(10, 3, funct)
        safe_intersection_priority(12, 2, 2, funct)
        safe_intersection_priority(13, 3, 3, funct)
        safe_passing(15, 2, 4, funct)
        safe_passing(16, 3, 4, funct)
        safe_passing(17, 4, 4, funct)

def run_all_test_cases():
    """
    Runs the set of all available test cases.
    """
    for msg, funct in zip(EVALUATOR_MSGS, EVALUATORS):
        print(BAR_STR, msg, BAR_STR)
        # Test 1
        left_right_test(1, funct)
        # Test 2
        same_name_test(2, funct)
        # Test 3
        one_lane_follow_test(3, 3, 3, funct)
        one_lane_follow_test(4, 3, 6, funct)
        one_lane_follow_test(5, 3, 9, funct)
        one_lane_follow_test(6, 3, 12, funct)
        one_lane_follow_test(7, 3, 15, funct)
        one_lane_follow_test(8, 3, 18, funct)
        # Test 4
        hazard_test(9, 2, funct)
        hazard_test(10, 3, funct)
        hazard_test(11, 4, funct)
        # Test 5
        safe_intersection_priority(12, 2, 2, funct)
        safe_intersection_priority(13, 3, 3, funct)
        safe_intersection_priority(14, 4, 4, funct)
        # Test 6
        safe_passing(15, 2, 4, funct)
        safe_passing(16, 3, 4, funct)
        safe_passing(17, 4, 4, funct)
        safe_passing(18, 5, 4, funct)
        # Test 7
        join_platoon(19, 3, 2, 5, funct)
        join_platoon(20, 3, 3, 5, funct)
        join_platoon(21, 3, 4, 5, funct)
        join_platoon(22, 3, 5, 5, funct)

def create_parser():
    parser = argparse.ArgumentParser(description="Checker experiment runner")

    # Mode flags
    mode = parser.add_mutually_exclusive_group(required=False)
    mode.add_argument("--quick", action="store_true", help="Run the quick reproduction subset")
    mode.add_argument("--all", dest="run_all", action="store_true", help="Run the full experiment suite")

    # Custom parameters (used only when neither --quick nor --all is passed)
    parser.add_argument("--road_length", type=int, help="Road length for a custom test case")
    parser.add_argument("--road_width", type=int, help="Road width for a custom test case")
    parser.add_argument("--prop", dest="props", action="append", default=[], help="Proposition symbol (repeatable).")
    parser.add_argument("--nom", dest="noms", action="append", default=[], help="Nominal symbol (repeatable).")
    parser.add_argument("--assumptions", type=str, help="Path to assumptions file")
    parser.add_argument("--conclusions", type=str, help="Path to conclusions file")
    parser.add_argument("--max_trace_length", type=int, help="Maximum trace length")
    parser.add_argument("--show_traces", type=int, choices=[0, 1], help="Whether to print traces (0/1)")
    parser.add_argument("--checker", type=str, choices=["optimized", "baseline", "motion"], help="Checker implementation")

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    # Mode A/B
    if args.quick:
        return run_quick_test_cases()
    if args.run_all:
        return run_all_test_cases()

    # Mode C: custom run (validate required fields)
    required = [
        "road_length",
        "road_width",
        "assumptions",
        "conclusions",
        "max_trace_length",
        "show_traces",
        "checker",
    ]

    missing = [r for r in required if getattr(args, r) is None]
    if missing:
        parser.error(
            "No mode selected. Use --quick or --all, OR provide a custom test case with: "
            + " ".join(f"--{m} ..." for m in missing)
        )

    road_length = int(getattr(args, 'road_length'))
    road_width = int(getattr(args, 'road_width'))
    max_trace_length = int(getattr(args, 'max_trace_length'))

    if int(getattr(args, 'max_trace_length')) == 1:
        show_traces = True
    else:
        show_traces = False

    if getattr(args, 'checker') == 'baseline':
        checker = evaluate_baseline
    elif getattr(args, 'checker') == 'optimized':
        checker = evaluate_optimized1
    else:
        checker = evaluate_optimized2

    path = Path(getattr(args, 'assumptions'))
    assumptions = []

    if not path.exists():
        raise FileNotFoundError("Assumptions file not found.")

    try:
        with path.open("r", encoding="utf-8") as f:
            assumptions = [line.strip() for line in f if line.strip()]
    except OSError:
        raise RuntimeError("Error reading assumptions file.")

    path = Path(getattr(args, 'conclusions'))
    conclusions = []
    if not path.exists():
        raise FileNotFoundError("Conclusions file not found.")

    try:
        with path.open("r", encoding="utf-8") as f:
            conclusions = [line.strip() for line in f if line.strip()]
    except OSError:
        raise RuntimeError("Error reading assumptions file.")

    if not conclusions:
        raise ValueError("No conclusions found in the file.")

    return run_evaluator(1, args.props, args.noms, assumptions, conclusions, (road_length, road_width), max_trace_length, show_traces, checker)


if __name__ == '__main__':
    sys.exit(main())

