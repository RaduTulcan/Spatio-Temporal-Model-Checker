from itertools import product
from checkers.SpatioTemporalEvaluatorUtils import satisfying_points, powerset
from checkers.optimized_version.OptimizedEvaluatorUtils import parse_static_car, parse_fixed_offset, \
    parse_fixed_movement, strip_parentheses
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from parsers.HybridSpatioTemporalFormulaParser import HybridSpatioTemporalParser, tokenize


def divide_cars_in_types(assumptions: list[str]) -> tuple[list[str], dict, dict, list[str]]:
    """
    Based on the given assumption formulas, cars are divided into static cars, dependent cars
    or fixed movement cars.

    :param assumptions: the list of assumption formulas
    :return: the static, dependent and fixed movement cars
    """

    static_cars: list[str] = []
    dependent_cars: dict = {}
    fixed_movement_cars: dict = {}
    dependent_car_names: list[str] = []
    fixed_movement_car_names: list[str] = []
    remaining_assumptions: list[str] = []

    for a in assumptions:
        consumed: bool = False
        a_fml: HybridSpatioTemporalFormula = HybridSpatioTemporalParser(tokenize(a)).parse()

        # car is static
        static_car: str = parse_static_car(a)

        if static_car:
            static_cars.append(static_car)
            consumed = True

        # car is dependent on another
        reference_car: str
        dependent_car: str
        dependent_offset: str
        reference_car, dependent_car, dependent_offset = parse_fixed_offset(a)

        if reference_car and dependent_car and dependent_offset:
            dependent_car_names.append(dependent_car)

            if reference_car not in dependent_cars.keys():
                dependent_cars[reference_car] = []
            dependent_cars[reference_car].append((dependent_car, dependent_offset))
            consumed = True

        # car has a fixed movement
        fixed_movement_car: str
        self_offsets: list[tuple[int, int]]
        fixed_movement_car, self_offsets = parse_fixed_movement(a_fml)

        if fixed_movement_car and self_offsets:
            fixed_movement_car_names.append(fixed_movement_car)

            if fixed_movement_car not in fixed_movement_cars.keys():
                fixed_movement_cars[fixed_movement_car] = []
            fixed_movement_cars[fixed_movement_car].extend(self_offsets)
            consumed = True

        if not consumed:
            remaining_assumptions.append(a)

    return static_cars, dependent_cars, fixed_movement_cars, remaining_assumptions


def build_adjacency(dependencies: dict) -> dict:
    """
    Creates a dictionary with cars as entries and dependent cars as values, including relative positions.

    :param dependencies: the dictionary of dependent cars
    :return: a dictionary with cars as key and dependent cars, including relative positions, as values
    """
    adjacency_graph: dict = {}
    for parent, children in dependencies.items():
        adjacency_graph.setdefault(parent, [])
        for child, (dx, dy) in children:
            adjacency_graph.setdefault(child, [])
            adjacency_graph[parent].append((child, (dx, dy)))
            adjacency_graph[child].append((parent, (-dx, -dy)))
    return adjacency_graph


def compute_components(adjacency_graph: dict) -> list[dict]:
    """
    Builds the dependent components of the dependent cars. All cars whose movement is dependent on
    other cars belong to the same dependent component.

    :param adjacency_graph: a dictionary with cars as key and dependent cars, including relative positions, as values
    :return: a list of dictionaries representing dependent components
    """
    components: list[dict] = []
    visited: set = set()

    for start in adjacency_graph.keys():
        if start in visited:
            continue

        relative_pos: dict = {start: (0, 0)}
        stack: list[dict] = [start]
        ok: bool = True

        while stack and ok:
            node: dict = stack.pop()
            node_pos_x: int
            node_pose_y: int
            node_pos_x, node_pose_y = relative_pos[node]

            for neighbor, (neighbor_dpos_x, neighbor_dpos_y) in adjacency_graph[node]:
                neighbor_pos_x, neighbor_pos_y = node_pos_x + neighbor_dpos_x, node_pose_y + neighbor_dpos_y

                if neighbor not in relative_pos:
                    relative_pos[neighbor] = (neighbor_pos_x, neighbor_pos_y)
                    stack.append(neighbor)
                else:
                    # consistency check
                    if relative_pos[neighbor] != (neighbor_pos_x, neighbor_pos_y):
                        ok = False
                        break

        if not ok:
            # return []  # inconsistent system -> no grids at all
            raise Exception("The given dependency formulas create a contradiction")

        components.append(relative_pos)
        visited.update(relative_pos.keys())

    return components


def placements_for_component(dependent_component: dict, grid_x: int, grid_y: int) -> list[dict]:
    """
    Generates all possible placements of the car in a dependent component within the grid.

    :param dependent_component: a dependent component
    :param grid_x: the number of rows in the grid
    :param grid_y: the number of columns in the grid
    :return: a list of all placement of the cars belonging to the given dependent component within the grid
    """
    xs: list[int] = [x for (x, _) in dependent_component.values()]
    ys: list[int] = [y for (_, y) in dependent_component.values()]
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    tx_min: int = -min_x
    tx_max: int = (grid_x - 1) - max_x
    ty_min: int = -min_y
    ty_max: int = (grid_y - 1) - max_y

    placements: list[dict] = []
    for tx in range(tx_min, tx_max + 1):
        for ty in range(ty_min, ty_max + 1):
            placement = {
                car: (x + tx, y + ty) for car, (x, y) in dependent_component.items()
            }
            placements.append(placement)
    return placements


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


def filter_state_assumptions(assumptions: list[str]) -> tuple[list[str], list[str]]:
    """
    Divides the list of assumptions into state assumptions and non-state assumptions.
    State assumptions can be evaluated with respect to a single grid.

    :param assumptions: the list of assumption
    :return: a list of state assumptions, and a list of non-state assumptions
    """
    state_assumptions: list[str] = []
    remaining_assumptions: list[str] = []
    for a in assumptions:
        if is_state_formula_string(a):
            state_assumptions.append(a)
        else:
            remaining_assumptions.append(a)
    return state_assumptions, remaining_assumptions


def test_state_assumptions(grid_size: tuple[int, int], trace: list[dict],
                           parsed_assumptions: list[HybridSpatioTemporalFormula]) -> bool:
    """
    Checks whether a list of state assumptions hold within the given grid.

    :param grid_size: the grid size
    :param trace: the grid the state assumptions have to be evaluated against
    :param parsed_assumptions: the list of state assumptions
    :return: true if all assumptions hold at every point in the given grid, false otherwise
    """
    points: list[tuple[int, int]] = [(i, j) for i in range(grid_size[0]) for j in range(grid_size[1])]
    for fml in parsed_assumptions:
        for p in points:
            if not fml.evaluate(trace, p, grid_size):
                return False
    return True


def generate_grids(grid_size: tuple[int, int], propositions: list[str], nominals: list[str], components: list[dict],
                   state_assumptions: list[HybridSpatioTemporalFormula]) -> dict:
    """
    Generates all possible start grids of the given grid size, propositions and nominals, and with respect to the given state assumptions.

    :param grid_size: the size of the grid
    :param propositions: the list of propositions
    :param nominals: the list of nominals
    :param components: the list of dependent car components
    :param state_assumptions: the list of state assumptions
    :return: all possible placement of the propositions and nominals in the grid w.r.t. the given assumptions
    """
    constrained_cars = set()

    for comp in components:
        constrained_cars.update(comp.keys())

    if components is None:
        raise Exception("The given dependency formulas create a contradiction")

    # generate placements for dependent cars
    component_placements = []

    for comp_rel_pos in components:
        pl = placements_for_component(comp_rel_pos, grid_size[0], grid_size[1])

        if not pl:
            return
        component_placements.append(pl)

    # if no components, treat as one empty choice
    if not component_placements:
        component_placements = [[{}]]

    # generate all points found in the bounding box
    points = [(i, j) for i in range(grid_size[0]) for j in range(grid_size[1])]

    # generate all placements for independent cars
    free_cars = [c for c in nominals if c not in constrained_cars]
    free_car_placements = [points for _ in free_cars]

    # generate all possible placements for each proposition
    prop_placements = [list(powerset(points)) for _ in propositions]

    for comp_placement in product(*component_placements):
        car_pos = {}
        for placement in comp_placement:
            for c, pos in placement.items():
                if c in car_pos and car_pos[c] != pos:
                    break
                car_pos[c] = pos
        else:
            # place free cars
            free_iter = product(*free_car_placements) if free_cars else product([()], )
            for free_positions in free_iter:
                all_car_pos = dict(car_pos)
                for c, pos in zip(free_cars, free_positions):
                    all_car_pos[c] = pos

                # assign propositions
                prop_iter = product(*prop_placements) if propositions else product([()], )
                for prop_choice in prop_iter:
                    grid = {}

                    # propositions -> list of positions (possibly empty)
                    if propositions:
                        for p, subset in zip(propositions, prop_choice):
                            grid[p] = list(subset)

                    # cars -> single position
                    for c, pos in all_car_pos.items():
                        grid[c] = pos

                    # check if the generated grid satisfies the state assumptions
                    if test_state_assumptions(grid_size, [grid], state_assumptions):
                        yield grid


def generate_traces(grid_size: tuple[int, int], propositions: list[str], nominals: list[str], static_cars: list[str],
                    dependent_cars: dict, fixed_movement_cars: dict,
                    state_assumptions: list[HybridSpatioTemporalFormula], trace_length: int) -> list[dict]:
    """
    Generates all possible traces.

    :param grid_size: the size of the grid
    :param propositions: the list of propositions
    :param nominals: the list of nominals
    :param static_cars: the list of static car
    :param dependent_cars: the dictionary of dependent cars
    :param fixed_movement_cars: the dictionary of fixed movement cars
    :param state_assumptions: the list of parsed assumption formulas
    :param trace_length: the maximal length of the traces to be generated
    :return:
    """

    # build dependency graph between dependent cars
    adj = build_adjacency(dependent_cars)

    # dependent components in the dependency graph with relative positions
    components = compute_components(adj)

    if components is None:
        return []

    dep_cars = [x for xs in components for x in xs.keys()]

    independent_cars = set(nominals) - set(static_cars) - set(dep_cars) - set(fixed_movement_cars)

    for grid in generate_grids(grid_size, propositions, nominals, components, state_assumptions):
        if trace_length == 1:
            yield [grid]
        else:
            # a static car cannot have a movement
            for s in static_cars:
                if s in fixed_movement_cars.keys():
                    yield []
                    return

            # if a component has a static car, no dependent car can have a fixed movement
            for c in components:
                if len(set(static_cars) & set(c.keys())) != 0 and len(
                        set(c.keys()) & set(fixed_movement_cars.keys())) != 0:
                    yield []
                    return

            # if cars in dependent components also are fixed movement cars, they must have at least a common relative movement
            for c in components:
                fixed_movement_cars_in_c = list(set(c.keys()).intersection(set(fixed_movement_cars.keys())))

                # if entries exist but no common relative movements - discard movement
                if len(fixed_movement_cars_in_c) > 0:
                    allowed_moves = fixed_movement_cars[fixed_movement_cars_in_c[0]]

                    for i in range(1, len(fixed_movement_cars_in_c)):
                        allowed_moves = set(allowed_moves).intersection(set(fixed_movement_cars_in_c[i]))

                    if len(allowed_moves) == 0:
                        yield []
                        return

            yield from extend_trace(grid_size, propositions, static_cars, dependent_cars, components,
                                    fixed_movement_cars, independent_cars, state_assumptions, 1, trace_length, grid,
                                    [grid])


def check_in_bound(grid_size: tuple[int, int], point: tuple[int, int]) -> bool:
    """
    Checks whether the coordinates of a point are within the grid bounds.

    :param grid_size: the size of the grid
    :param point: the coordinates of the point
    :return: true if point within the grid bounds, false otherwise
    """
    return 0 <= point[0] < grid_size[0] and 0 <= point[1] < grid_size[1]


def add(p: tuple[int, int], d: tuple[int, int]) -> tuple[int, int]:
    """
    Adds two points component-wise.

    :param p: the first point
    :param d: the second point
    :return: the component-wise addition of the two points
    """
    return p[0] + d[0], p[1] + d[1]


def combine_placements(grid_size: tuple[int, int], curr_grid: dict, static_car_names: list[str], components: list[dict],
                       fixed_movement_car_names: list[str],
                       independent_car_names: list[str], moves: dict, propositions: list[str],
                       state_assumptions: list[HybridSpatioTemporalFormula]) -> dict:
    """
    Combines all possible placements of nominals and propositions. The placements of nominals are made with respect to the type of cars they represent, i.e.
    static car, dependent car or fixed movement car.

    :param grid_size: the size of the grid
    :param curr_grid: the  current grid
    :param static_car_names: the names of the static cars
    :param components: the dependent components
    :param fixed_movement_car_names: the list of names of the fixed movement cars
    :param independent_car_names: the names of the independent cars
    :param moves: the available moves for each car
    :param propositions: the list of propositions
    :param state_assumptions: the list of state assumptions
    :return: a filled grid with the given nominals and propositions
    """

    # placements of static cars
    static_car_moves: list[list[tuple[int, int]]] = []
    for c in static_car_names:
        allowed_moves: list[tuple[int, int]] = [add(curr_grid[c], m) for m in moves[c] if
                                                check_in_bound(grid_size, add(curr_grid[c], m))]
        static_car_moves.append(allowed_moves)

    # placement of dependent cars
    dep_cars: list[str] = [x for xs in components for x in xs.keys()]
    fixed_car_moves: list[list[tuple[int, int]]] = []
    for c in (set(fixed_movement_car_names) - set(dep_cars)):
        allowed_moves: list[tuple[int, int]] = [add(curr_grid[c], m) for m in moves[c] if
                                                check_in_bound(grid_size, add(curr_grid[c], m))]
        fixed_car_moves.append(allowed_moves)

    independent_car_moves: list[list[tuple[int, int]]] = []
    for c in independent_car_names:
        allowed_moves: list[tuple[int, int]] = [add(curr_grid[c], m) for m in moves[c] if
                                                check_in_bound(grid_size, add(curr_grid[c], m))]
        independent_car_moves.append(allowed_moves)

    points: list[tuple[int, int]] = [(i, j) for i in range(grid_size[0]) for j in
                                     range(grid_size[1])]
    prop_placements: list[list] = [list(powerset(points)) for _ in propositions]

    dependent_components_placements = [[] for _ in components]
    for j in range(0, len(components)):
        members = list(components[j].keys())

        for mov in moves[members[0]]:
            all_in_grid: bool = True
            pos: list[tuple[int, int]] = []
            for i in range(0, len(members)):
                if not check_in_bound(grid_size, add(curr_grid[members[i]], mov)):
                    all_in_grid = False
                    break
            if all_in_grid:
                for i in range(0, len(members)):
                    pos.append(add(curr_grid[members[i]], mov))
                dependent_components_placements[j].append(pos)

    # simulate itertools.product when array empty
    dependent_components_choices = []
    if not dependent_components_placements:
        dependent_components_choices = [[]]
    else:
        for p in product(*dependent_components_placements):
            flat = []
            for inner in p:
                flat.extend(inner)
            dependent_components_choices.append(flat)

    for static_car_choice in product(*static_car_moves):  # static_car_placements:
        for fixed_car_choice in product(*fixed_car_moves):  # fixed_car_placements:
            for independent_car_choice in product(*independent_car_moves):  # independent_car_placements:
                for dependent_component_choice in dependent_components_choices:
                    for prop_choice in product(*prop_placements):
                        placement: dict = {}

                        for name, pl_choice in zip(static_car_names, static_car_choice):
                            placement[name] = pl_choice

                        for name, pl_choice in zip(set(fixed_movement_car_names) - set(dep_cars), fixed_car_choice):
                            placement[name] = pl_choice

                        for name, pl_choice in zip(independent_car_names, independent_car_choice):
                            placement[name] = pl_choice

                        for name, subset in zip(propositions, prop_choice):
                            placement[name] = list(subset)

                        for name, pl_choice in zip(dep_cars, dependent_component_choice):
                            placement[name] = pl_choice

                        for fml in state_assumptions:
                            for p in points:
                                if not fml.evaluate([placement], p, grid_size):
                                    break
                            else:
                                continue
                        yield placement


def extend_trace(grid_size: tuple[int, int], propositions: list[str], static_cars: list[str], dependent_cars: dict,
                 components: list[dict], fixed_movement_cars: dict,
                 independent_cars: list[str], state_assumptions: list[HybridSpatioTemporalFormula],
                 curr_trace_length: int, max_trace_length: int, prev_grid: dict, trace: list[dict]) -> list[dict]:
    """
    Extends the trace by an additional grid.

    :param grid_size: the size of the grid
    :param propositions: the list of propositions
    :param static_cars: the list of static cars
    :param dependent_cars: the dictionary of dependent cars
    :param components: the list od dependent components
    :param fixed_movement_cars: the dictionary of fixed movement cars
    :param independent_cars: the list of independent cars
    :param state_assumptions: the list of state assumptions
    :param curr_trace_length: the current length of the trace
    :param max_trace_length: the maximal length of the trace
    :param prev_grid: the previous state in the trace
    :param trace: the trace to extend
    :return: the extended trace
    """
    if curr_trace_length <= max_trace_length:
        yield trace
        if curr_trace_length == max_trace_length:
            return
    else:
        raise Exception("Current trace length exceeded maximum trace length")

    moves: dict = {}

    # static cars are placed in the same position in the next time instance
    for s in static_cars:
        moves[s] = [(0, 0)]

    # all possible movements within grid bounds
    all_deltas: list[tuple[int, int]] = [
        (dy, dx)
        for dy in range(-(grid_size[0] - 1), grid_size[0])
        for dx in range(-(grid_size[1] - 1), grid_size[1])
    ]

    # place dependent cars
    for c in components:
        # if we have a static car in the component, all cars must be static (in the wrapper function it is already
        # checked that no dependent components have static and fixed movement cars)
        if len(set(static_cars) & set(c.keys())) > 0:
            for d in c.keys():
                moves[d] = [(0, 0)]

        else:
            # get common fixed movements for cars in component
            fixed_movement_cars_in_c: list[tuple[int, int]] = list(
                set(c.keys()).intersection(set(fixed_movement_cars.keys())))

            # if entries exist but no common relative movements - discard movement
            if len(fixed_movement_cars_in_c) > 0:
                allowed_moves: set[tuple[int, int]] = fixed_movement_cars[fixed_movement_cars_in_c[0]]

                for i in range(1, len(fixed_movement_cars_in_c)):
                    allowed_moves = set(allowed_moves).intersection(set(fixed_movement_cars_in_c[i]))

                for car in c.keys():
                    moves[car] = allowed_moves

            else:
                # if no entries in fixed movement - all movements are possible
                for car in c.keys():
                    moves[car] = all_deltas

    # place fixed movement cars
    dep_cars: list[str] = [x for xs in components for x in xs.keys()]
    for c in set(fixed_movement_cars) - set(dep_cars):
        moves[c] = fixed_movement_cars[c]

    # place independent cars
    for c in independent_cars:
        moves[c] = all_deltas

    # combine placements
    for placement in combine_placements(grid_size, prev_grid, static_cars, components, list(fixed_movement_cars.keys()),
                                        independent_cars, moves, propositions, state_assumptions):
        # new_trace: list[dict] = trace + [placement]
        # check if the generated placement satisfies the state assumptions
        if test_state_assumptions(grid_size, [placement], state_assumptions):
            yield from extend_trace(grid_size, propositions, static_cars, dependent_cars, components,
                                    fixed_movement_cars,
                                    independent_cars, state_assumptions, curr_trace_length + 1, max_trace_length,
                                    placement,
                                    trace + [placement])


def evaluate(propositions: list[str], nominals: list[str], assumptions, conclusions, grid_size: tuple[int, int],
             max_trace_length: int,
             show_traces: bool):
    """
    Evaluates the given formulas against all generated traces.

    :param propositions: the list of propositions
    :param nominals: the list of nominals
    :param assumptions: the list of assumptions
    :param conclusions: the list of conclusions
    :param grid_size: the size of the grid
    :param max_trace_length: the maximal trace length
    :param show_traces: whether satisfying traces should be shown in the console or not
    """

    static_cars, dependent_cars, fixed_movement_cars, remaining_assumptions = divide_cars_in_types(assumptions)
    state_assumptions, remaining_assumptions = filter_state_assumptions(remaining_assumptions)
    parsed_state_assumptions = [HybridSpatioTemporalParser(tokenize(fml)).parse() for fml in state_assumptions]

    # conjunction of assumptions and conclusion
    input_formula_string: str = "&".join([*("(" + x + ")" for x in conclusions),
                                          *("(" + x + ")" for x in remaining_assumptions)])

    # parse the input formula
    parsed_formula: HybridSpatioTemporalFormula = HybridSpatioTemporalParser(tokenize(input_formula_string)).parse()

    counter_sat = 0
    counter_gen = 0
    for t in generate_traces(grid_size, propositions, nominals, static_cars, dependent_cars, fixed_movement_cars,
                             parsed_state_assumptions, max_trace_length):
        sat_points = satisfying_points(parsed_formula, t, grid_size)

        if sat_points:
            if show_traces:
                print("\t |Satisfying trace #", counter_sat, " with satisfying points: ", sat_points)
                print("\t |--------------------------------------------------------------------")
                print("\t |", t, "\n")
            counter_sat = counter_sat + 1
        counter_gen = counter_gen + 1
    print("|Sat:", counter_gen)
    print("|TraceX:", counter_sat)
