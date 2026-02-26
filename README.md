
# Hybrid Spatiotemporal Model Checker
**Paper Title:** Hybrid Spatiotemporal Logic for Automotive Applications: Modeling and Model-Checking 

**Authors:** Radu-Florin Tulcan, Rose Bohrer, Yoàv Montacute, Kevin Zhou, Yusuke Kawamoto, and Ichiro Hasuo

## Version Information
This project has been tested with Python v3.9 and v3.12

## Description
This project is the implementation of the model checker for the _Hybrid Spatiotemporal Logic for
Automotive Safety_. This file contains metadata about the implementation, information about the project structure,
and about the parsable syntax of our logic. It also contains information about how the different versions of our model checker
can be used, as well as some insights about the experiments conducted, which highlight the capabilities of our logic and model
checker.

## Basic Usage
Our artifact is provided as a Docker image. We first document the usage syntax in general, then provide recommended step-by-step instructions for AEC.

### General Usage Syntax
The general usage syntax is:
```
docker run --rm paper-artifact:latest python ExperimentRunner.py [-h] [--quick | --all] [--road_length ROAD_LENGTH] [--road_width ROAD_WIDTH] [--prop PROPS] [--nom NOMS]
                           [--assumptions ASSUMPTIONS] [--conclusions CONCLUSIONS] [--max_trace_length MAX_TRACE_LENGTH] [--show_traces {0,1}]      
                           [--checker {optimized,baseline,motion}]
```
We allow three modes of operation:
- ``quick``: this mode runs the test suit with the smaller test cases, totalling a run-time of around 20 minutes
- ``all``: this mode runs all test cases included in the paper, with an approximate run-time of around 3.5 - 4 hours
- custom mode: this mode allows custom experimentation of our model checkers using the following parameters
  - ``road_length`` (positive number): the length of the grid structure
  - ``road_width`` (positive number): the width of the grid structure
  - ``prop`` (string): a proposition used in the custom formulas. This argument can occur multiple times.
  - ``assumptions`` (string): a path to a file containing the formulas used as assumptions, where each formula is written in a separate line. For convenient usage, the artifact contains a file ``assumptions.txt`` that can be used as input.
  - ``conclusions`` (string): a path to a file containing the formulas used as conclusion, where each formula is written in a separate line. For convenient usage, the artifact contains a file ``assumptions.txt`` that can be used as input.
  - ``max_trace_length`` (positive number): maximal length of traces that the checker should evaluate the formulas against
  - ``show_traces`` (0/1): whether the satisfying traces should be displayed in the commandline or not
  - ``checker`` (optimized/baseline/motion): the checker version

**Example:** 
```
docker run --rm paper-artifact:latest python ExperimentRunner.py \
    --road_length 2 \
    --road_width 3 \
    --prop a \
    --prop b \
    --assumptions assumptions.txt \
    --conclusions conclusions.txt \
    --max_trace_length 3 \
    --show_traces 1 \
    --checker optimized 
```

### Step-by-step Usage Instructions (for AEC)
First, load the Docker image from the provided archive file:
'docker load < artifact.tar.gz'

Second, run the artifact in quick mode, which is the default mode. This took about 20 minutes on an author's workstation.
'docker run --rm paper-artifact:latest python ExperimentRunner.py --quick'

Check the correctness of the output by following the instructions in the following subsection "Interpreting the Output (AEC)".

Third, run the artifact in full mode. This took 3.5-4 hours on an author's workstation.
'docker run --rm paper-artifact:latest python ExperimentRunner.py --all'

Check the correctness of the output by following the instructions in the following subsection "Interpreting the Output (AEC)".
This completes the basic evaluation. If a more thorough evaluation is desired, see section "Custom Usage and Logic Syntax" for 
instructions on writing and testing new formulas of your own, and see section "Inspecting Source Code and Folder Structure" for
instructions on code-reviewing the source code. See section "Experiments" for detailed explanations of how we modeled each major test.

### Interpreting the Output (AEC)
 NOTE TO AEC : We revised the output to match the table format suggested by the reviewers. We apologize for not doing so earlier.
 This section describes the revised output format.

The modes --quick and --all should be checked for correctness against Table 1.
Mode --quick evaluates tests 1,2,3,4,5,6,9,10,12,13,15,16,17 and 
--all evaluates all tests. Both flags test all three checkers.

The output will be displayed in delimiter-separated values (semicolon-separated) format.
A header is displayed, describing all columns of the table.
Tests are run one at a time, i.e., all three algorithms are run for the first test before proceeding to the second.
Once all three algorithms complete, the next row of the table prints.
Printed output should appear at least once every 30 minutes (much less for fast test cases).

The following table is an example run by one of the authors.

```
Test; Nominals; Grid; Len; #Sat; #Trace1; #Trace2; #Trace3; Time1; Time2; Time3
-------------------------------------------------------------------------------
1; 1; (3, 3); 3; 819; 819; 819; 819; 0.03716773200000034; 0.03712973300000044; 0.03992743000w000587
2; 2; (3, 3); 3; 819; 538083; 819; 538083; 3.7923480649999988; 0.015061762000001977; 4.946865924000008
3; 2; (3, 1); 3; 9; 819; 258; 270; 0.014349297999999067; 0.01910730299999841; 0.006025803999989421
4; 2; (6, 1); 3; 30; 47988; 27930; 4752; 1.4389156609999958; 3.2547366950000054; 0.14877714799999353
5; 2; (9, 1); 3; 51; 538083; 378504; 24786; 23.04235685900001; 62.408909518000016; 1.0796061880000138
6; 2; (12, 1); 3; 72; 3006864; 2317524; 79488; 164.72859127499999; 499.78983279100004; 4.517372851999994
9; 2; (2, 2); 2; 32; 65792; 65792; 65792; 0.45820572799993897; 0.4590834310000673; 0.5815292339999587
10; 2; (2, 2); 3; 2080; 16843008; 16843008; 16843008; 107.26402025599998; 106.9159558660001; 139.56479126900012
12; 2; (2, 2); 2; 6; 272; 156; 48; 0.007147589000169319; 0.010924726999974155; 0.003130738999971072
13; 2; (3, 3); 3; 24; 538083; 378504; 2754; 23.42363127700014; 56.464471282999966; 0.1858928480000941
15; 2; (4, 2); 2; 5; 4160; 812; 480; 0.150144482000087; 0.14052099000014096; 0.030547789000138437
16; 2; (4, 2); 3; 17; 266304; 22764; 6624; 10.060745548000114; 5.2045411530000365; 0.39718149399982394
17; 2; (4, 2); 4; 21; -; 637420; 88544; -; 183.64836666399992; 5.736927527999796
```

The output columns Time1,Time2,Time3 will not match Table 1 exactly. 
The authors observed significant variation between successive trials.
For example, the example was produced while many other processes were running, leading to slower results compared to Table 1.
Times should be multiplied by a constant factor if your machine is faster or slower.

If a test does not finish in 10 minutes, it will time out. This corresponds to "-" in the columns TraceX and TimeX.
The column "Sat" is an output, but should be the same for all three algorithms.
If all three algorithms time out, we write "-" in the Sat column. 
If at least one algorithm terminates, we use the "Sat" value from the terminating algorithm(s).

## Custom Usage and Logic Syntax
Our artifact allows you to input custom models of your choice, which is a good opportunity for the AEC to test edge
cases and scalability independently of the authors' test suite. To run the artifact with a custom model, you must
provide all of the following options: "road_length", "road_width", "max_trace_length", "show_traces", "checker", 
"assumptions", "conclusions".

The following example provides reasonable default values which you can modify to your liking:
```
docker run --rm paper-artifact:latest python ExperimentRunner.py \
    --road_length 2 \
    --road_width 3 \
    --assumptions assumptions.txt \
    --conclusions conclusions.txt \
    --max_trace_length 3 \
    --show_traces 1 \
    --checker motion
```
In contrast to the modes --quick and --all, only one checker is run, determined by the value of --checker.
If --show_traces 1 is set, the exact contents of all satisfying traces are printed. This information is 
valuable for checking correctness in full detail, but may be overwhelming if many traces exist.
Set --show_traces 0 to avoid printing this information.

The arguments --assumptions and --conclusions are paths to files containing your assumption and conclusion 
formulas, which are the heart of your custom model. The formula syntax of these files follows the one from the paper.
The table below consists of the operators permitted and the corresponding symbols parsable by the model checker:

Note that both plaintext ASCII notations and more advanced Unicode notations are supported.

| Operator               | Symbols  | Operator            | Symbols |
|------------------------|----------|---------------------|---------|
| Logical Truth          | ⊤ or 1   | Spatial Left        | Left    |
| Logical Falsity        | ⊥ or 0   | Spatial Right       | Right   |
| Logical Negation       | ¬ or !   | Temporal Next       | X       |
| Logical And            | ∧ or &   | Temporal Eventually | F       |
| Logical Or             | \|       | Temporal Always     | G       |
| Logical Implication    | → or ->  | Temporal Until      | U       |
| Logical Bi-implication | ↔ or <-> | At Operator         | @       |
| Spatial Front          | Front    | Bind Operator       | ↓ or :  |
| Spatial Back           | Back     |

A major syntax restriction is that every nominal name must start with 'z', optionally followed by digits and underscores.
That is, nominals must match the regular expression `z[0-9_]*`.

Most practical test models will not use propositions, which we mainly used to demonstrate the performance impact of nominals.
However, if you use them, they must match the regular expression `[a-y][a-y0-9_]*` and must be specified with the option --prop.

Modeling new scenarios successfully with this syntax takes some practice; the interaction between temporal and hybrid operators is subtle.
The provided test cases, whose source code is in ExperimentRunner.py, use the same syntax as user-provided models.
You are encouraged to consult the provided test cases as examples of how to use the syntax.

**Precedence relation:** The operators satisfy the following precedence relation: `↔ << → << | << ∧ << U << ¬, Left, Right, Back, Front, X, F, G, @, ↓`.

## Inspecting Source Code and Folder Structure
We document the project's folder structure to make code review easier.
The project contains multiple folders. Their contents are summarized in the list below:

- `checkers/baseline_version`: contains the implementation of the baseline model checker
- `checker/optimized_version`: contains the implementation of the two optimized versions of our model checker
- `formula_types`: contains all necessary classes and methods for the various operators of our logic and their evaluation
- `parsers`: includes parser code for the different components of our language
- `tests`: contains unit tests used to validate smaller components of the implementation before ExperimentRunner.py was completed.
- `ExperimentRunner.py`: contains the code for the experiments included in the paper and detailed [below](#experiments).

We aim for research-grade code, not production-grade. We make an effort to document key information, but we do not aim 
for user-friendly error messages and we permit significant code duplication, in part because this helps ensure that changes
to implementation details in the optimized algorithms do not change the "baseline" performance, which is supposed to be stable. 

The unit tests in the "tests" directory do not need to be run to evaluate the claims of the paper, but if you wish to run them, 
you can invoke the Python interpreter on any test file, with the repository root on your Python path.

### Experiments
The file `ExperimentRunner.py` contains the experiments conducted for our paper. This section will go over the experiments in detail.
This documentation helps explain why the test scenarios are modeled correctly and is also likely to be of use if you wish to
write your own custom models.

#### One Lane Follow

This scenario has been implemented in the function `one_lane_follow_test`. In this scenario test that one vehicle can safely follow another in the same lane.  `z0` is SV, `z1` is POV1, `z2` is a temporary variable. In this scenario we assume the following:
 
-  `@z0 !(Back 1)`: SV is initially at the start of the lane
-  `G (@z1 ↓z2 ((! X 1) | X @z1  (z2 | Back z2)))`: POV always moves forward or stays put
-  `G (@z0 ↓z2 ((! X 1) | X (@z0 ((!z1 & Back z2 ) | (z2 & Front z1) ))))`: SV always moves forward if safe, stays put if POV immediately ahead

The property we want to check is, whether these two vehicles collide. It can be expressed by `G(!(@z0 z1))`.

**_Usefulness_**: This is a minimal, practical scenario, that can be easily scaled as needed.

#### Safe Intersection with Priority
This scenario models a 4-way intersection where one road has priority over the other, so that only one vehicle needs to stop. We consider an (nxn) grid where the POV vehicle moves left-to-right without stopping.
The SV vehicle moves back to front and stops if POV is on track to collide. Here, `z0` is SV, `z1` is POV, `z2` is a temporary variable.
For this scenario we assume the following:

- `@z1 !(Left 1)`: POV starts somewhere on the left border
- `@z0 !(Back 1)`: SV starts somewhere on the bottom border
- `G (@z1 ↓z2 ((! X 1)| X @z1 (Left z2)))`: POV always moves left-to-right
- `G (@z0 ↓z2 ((! X 1)| X @z0 ((!z1 & Back z2) | (z2 & Front z1) )))`: moves bottom-to-top except it stops to avoid the other vehicle

In this scenario we also check for non-collision, expressed by `G(!(@z0 z1))`.

**_Usefulness_**: Since the grid scales quadratically, new, larger test cases can be generated easily. Furthermore, crossing an intersection allows us
to demonstrate a higher level of generality of our logic.

#### Safe Passing
In this section we consider the following scenario: On a two-lane road, POV moves forward at uneven speed. 
Initially SV moves forward at even speed. If it is ever directly behind POV, it swerves to left, 
then drives at high speed to overtake POV, swerves right, then drives normally. Concretely, the scenario is
divided into the following steps:
1. move forward initially (duration of >=0 timesteps)
2. swerve left (duration of 1 timestep)
3. drive forward fast (duration of >0 timesteps)
4. swerve right (duration of 1 timestep)
5. go forward at normal speed (duration is all remaining timesteps)

Furthermore, in this example, `z0` is SV, `z1` is POV, and `z2` a temporary variable. For modelling it, we used the following formulas:
- `G(@z1 !(Right 1))`: POV starts anywhere in right lane, stays in right lane
- `@z0 !(Right 1)`:  SV starts in the back
- `@z0 !(Back 1)`: SV starts in the right lane
- `G (@z1 ↓z2 ((! X 1) | X @z1  (z2 | Back z2)))`: POV moves forward or stays in place

Moreover, the following formula encodes the 5-step behavior described above:
`(φ1 U (φ2 & ((! X 1) | X (φ3 & ((! X 1) | X (φ3 U (φ4 & ((! X 1) | X G (φ5)))))))))`
with:
- `φ1:= (@z0 ↓z2 ((! X 1) | X @z0 (Back z2)))`: SV initially moves forward
- `φ2:= (@z0 ↓z2 ((Front z1) & ((! X 1)| X (@z0 (Back (Right z2))))))`: SV swerves left
- `φ3:= (@z0 ↓z2 ((! X 1)| X @z0 (Back (Back z2))))`: SV drives twice as fast
- `φ4:= (@z0 ↓z2 ((! X 1)| X @z0 (Back (Left z2))))`: SV swerves right when safe
- `φ5:= (@z0 ↓z2 ((! X 1) | X @z0 (Back z2)))`: SV drives normally
Note the pattern  P & X (P Until Q) is used to ensure Step 3 runs for at least one timestep

In this scenario we also check for non-collision, expressed by `G(!(@z0 z1))`.

**Usefulness:** This scenario represents a stress-test for the Until operator. This non-trivial example
Helps demonstrate the value of optimizing one vehicle when the other clearly cannot be optimized
(though we have other tests which demonstrate that same point).

#### Join Platoon
In this scenario, a platoon of POV cars are all traveling at constant speed. The SV is trying to join the platoon. 
It can join the platoon by switching lanes if the resulting position is both behind a car of the platoon and is safe.
Here, `z0` is SV and `z1-zn` are the n POVs. In the following, we write `|i in [1..n] P(i)` for an n-ary disjunction.
We assume the following formulas:
- `φ1:= @z0 !(Right 1)`: SV starts in the right lane
- `φ2:= G(@zi !(Left 1)) (for i in [1,n])`: POVs are always in left lane
- `φ3:= G(@z0 ↓z ((! X 1) | (X @z0((Back z)|`: SV, go forward any time, or
          `((|i in [1,n] Front zi)&(Right z)&(!(|i in [1,n] zi))))))` switch lane if safe
- `φ4:= G(@zi ↓z ((! X 1) | X (@zi (Back z)))) (for i in [1,n])`: Platoon cars move forward
And the conclusion is:
- `φ5:= G(@z0 !(|i in [1,n] zi))` Collision avoidance


**Usefulness:** Most other tests only scale the road while keeping the number of vehicles and the formulas the same. 
This test scales the number of vehicles and the size of the formulas, which allows us to evaluate a different aspect of scalability compared to the other test cases.

_Subtle note:_ We allow multiple cars in the platoon to have the same position as each other. We choose to see this as a feature instead of a bug, because it's equivalent
to testing all platoons of size *up to N* instead of size *exactly N*, e.g., if all cars in a 5-car platoon are in the same position, it functions as a 1-car platoon.
