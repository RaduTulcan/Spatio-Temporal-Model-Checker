import multiprocessing
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
#from checkers.baseline_version.evaluator_baseline.SpatioTemporalEvaluator import evaluate
#from checkers.optimized_version.evaluator_optimized.SpatioTemporalEvaluator1 import evaluate 
from checkers.optimized_version.evaluator_optimized.SpatioTemporalEvaluator2 import evaluate

from timeit import default_timer as timer 
# Rose apologizes to imperative programmers OTL
from functools import reduce

from parsers.HybridSpatioTemporalFormulaParser import HybridSpatioTemporalParser, tokenize


def evaluate_handler(propositions, nominals, assumptions, conclusions, grid_size, trace_max_length, show_traces):
   start: float = timer()
   evaluate(propositions, nominals, assumptions, conclusions, grid_size, trace_max_length, show_traces)
   end: float = timer()
   print("|Time elapsed:", end - start, "\n")
    
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
    TIMEOUT = 5    

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
    p = multiprocessing.Process(target=evaluate_handler,args=(propositions, nominals, assumptions, conclusions, grid_size, trace_max_length, show_traces))
    p.start()
    p.join(TIMEOUT)
    if p.is_alive():
        print("=====================   TIMED OUT ===========================")
        p.terminate()
        p.join()

def front_back_test(test_index: int):
    run_evaluator(test_index, [], ['z'], [], ["G(Left(Right(z)) <-> Right(Left(z)))"], (3,3), 3, False)

def same_name_test(test_index: int):
    run_evaluator(test_index, [], ['z', 'z1'], [], ["G (@z z1)"], (3, 3), 3, False)

# Test description: We test that one vehicle can safely follow another in the same lane. z0 is SV, z1 is POV1, z2 is a temporary variable. The first assumption says that POV brakes
# arbitrarily, sometimes staying still and other times moving forward. The second assumption says that SV follows POV1 as closely as possible without violating safety, i.e., we only
# stay in place if POV is directly ahead. The conclusion says the two vehicles never collide.
# Usefulness: We need a minimal, scalable "practical" example. This fills those requirements.
def one_lane_follow_test(test_index:int, road_length: int):
    run_evaluator(test_index, [], ['z0', 'z1'], 
        ["@z0 !(Back 1)", #SV is initially at the start of the lane
         "G (@z1 ↓z2 ((! X 1) | X @z1  (z2 | Back z2)))", #POV always moves forward or stays put
         "G (@z0 ↓z2 ((! X 1) | X (@z0 ((!z1 & Back z2 ) | (z2 & Front z1) ))))"] , #SV Always moves forward if safe, stays put if POV immediately ahead
         ["G(!(@z0 z1))"], (5,1), 3, False)

# Test description: We model a 4-way intersection where one road has priority over the other, so that only one need to stop. We consider an N by N grid where the POV vehicle moves 
# left-to-right without stopping. The SV moves back to front and stops if POV is on track to collide. z0 is SV, z1 is POV, z2 is temporary variable.
# First assumption says POV moves in a straight line, second assumption says SV brakes (only) when needed, conclusion is collision freedom
# Usefulness: The grid scales quadratically which allows us to generate large test cases easily. Crossing an intersection allows us to demonstrate a higher level of generality.
def safe_intersection_priority(test_index: int, grid_size: int):
    run_evaluator(test_index, [], ['z0', 'z1'], 
                  ["@z1 !(Left 1)", #z1 starts somewhere on the left border
                   "@z0 !(Back 1)", #z0 starts somewhere on the bottom border
                   "G (@z1 ↓z2 ((! X 1)| X @z1 (Left z2)))", #Moves left-to-right always
                   "G (@z0 ↓z2 ((! X 1)| X @z0 ((!z1 & Back z2) | (z2 & Front z1) )))"],  #Moves bottom-to-top except it stops to avoid other vehicle.
                   ["G(!(@z0 z1))"], (grid_size, grid_size), 3, False)

# Test description: In this two-lane scenario, POV1 moves forward at uneven speed. Initially SV moves forward at even speed. 
# If it is ever directly behind POV1, it swerves to left , then drives at high speed to overtake POV1, swerves right, then drives normally
# z0 is SV, z1 is POV
#
# The five steps are
# 1 move forward initially
# 2 swerve left
# 3 drive forward fast
# 4 swerve right
# 5 go forward at normal speed
# The duration of each step is
# Step 1: >=0 timesteps
# Step 2: 1 timestep
# Step 3: >0 timesteps
# Step 4: 1 timestep
# Step 5: all remaining timesteps.
# Note the pattern  P & X (P Until Q) is used to ensure Step 3 runs for at least one timestep
#
# Usefulness: Stress-tests the Until operator. "Non-trivial example". Helps demonstrate the value of optimizing one vehicle when the other clearly cannot be optimized 
# (though we have other tests which demonstrate that same point)
def safe_passing(test_index: int, road_length: int):
    # z0 initially moves forward
    first_forward = "(@z0 ↓z2 ((! X 1) | X @z0 (Back z2)))"
    # then swerves left to avoid z1
    dodge_left    = "(@z0 ↓z2 ((Front z1) & ((! X 1)| X (@z0 (Back (Right z2))))))"
    # then drives twice as fast
    fast_forward  = "(@z0 ↓z2 ((! X 1)| X @z0 (Back (Back z2))))"
    # then dodges back when safe
    dodge_right   = "(@z0 ↓z2 ((! X 1)| X @z0 (Back (Left z2))))"
    # then drives normally
    last_forward  = "(@z0 ↓z2 ((! X 1) | X @z0 (Back z2)))"
    run_evaluator(test_index, [], ['z0', 'z1'], 
                  ["G(@z1 !(Right 1))", # POV starts anywhere in right lane, stays in right lane
                   "@z0 !(Right 1)", # SV starts in back of right lane
                   "@z0 !(Back 1)",
                   "G (@z1 ↓z2 ((! X 1) | X @z1  (z2 | Back z2)))", #z1 moves forward or stays in place
                   "({} U ({} & ((! X 1) | X ({} & ((! X 1) | X ({} U ({} & ((! X 1) | X G ({})))))))))".format(first_forward,dodge_left,fast_forward,fast_forward,dodge_right,last_forward)], 
                   ["G(!(@z0 z1))"], (road_length, 2), 3, False)
    
# Test description: In this test, a platoon of POV cars are all traveling at constant speed. The SV is trying to join the platoon. It can join the platoon by switching lanes
# if the resulting position is both behind a car of the platoon and is safe.
# Usefulness: Most other tests only scale the road while keeping the number of vehicles and the formulas the same. This test scales the number of vehicles and the size of the formulas,
# which allows us to evaluate a different aspect of scalability compared to the other test cases.
# Subtle note: We allow multiple cars in the platoon to have the same position as each other. We choose to see this as a feature instead of a bug, because it's equivalent
# to testing all platoons of size *up to N* instead of size *exactly N*, e.g., if all cars in a 5-car platoon are in the same position, it functions as a 1-car platoon. 
def join_platoon(test_index: int, platoon_size: int, road_length: int):
    pov_noms = ["z"+str(i+1) for i in range(platoon_size)]
    noms = ["z0"] + pov_noms  # and z is a temporary
    no_collide = "!({})".format(reduce((lambda x, acc: x + "|" + acc), pov_noms))
    each_front = ["Front " + n for n in pov_noms]
    some_front = reduce((lambda x, acc: x + "|" + acc), each_front)
    sv_mov_assump = "G(@z0 ↓z ((! X 1) | (X @z0((Back z)|(({0})&(Right z)&({1}))))))".format(some_front, no_collide)
    sv_start_assump = "@z0 !(Right 1)"
    pov_start_assumps = [format("G(@z{0} !(Left 1))".format(str(i+1))) for i in range(platoon_size)]
    pov_mov_assumps = [format("G(@z{0} ↓z ((! X 1) | X (@z{0} (Back z))))".format(str(i+1))) for i in range(platoon_size)]
    assumps = [sv_start_assump, sv_mov_assump] + pov_mov_assumps + pov_start_assumps
    postcond = "G(@z0 ({}))".format(no_collide)
    run_evaluator(test_index, [], noms, assumps, [postcond], (road_length, 2), 3, False)

if __name__ == '__main__':
    # Test 1
    front_back_test(1)
    # Test 2
    same_name_test(2)
    #Test 3
    one_lane_follow_test(3, 5)
    #Test 4
    safe_intersection_priority(4, 3)
    #Test 5
    safe_passing(5, 4)
    #Test 6
    join_platoon(6, 2, 2)
