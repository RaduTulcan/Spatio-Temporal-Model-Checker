from itertools import product
from checkers.optimized_version.OptimizedEvaluatorUtils import parse_static_car, parse_fixed_offset, \
    parse_fixed_movement, powerset
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from parsers.HybridSpatioTemporalFormulaParser import HybridSpatioTemporalParser, tokenize


def divide_cars_in_types(assumptions, nominals):
    static_cars = []
    dependent_cars = {}
    fixed_movement_cars = {}
    dependent_car_names = []
    fixed_movement_car_names = []

    for a in assumptions:
        a_fml = HybridSpatioTemporalParser(tokenize(a)).parse()
        # car is static
        static_car = parse_static_car(a)
        if static_car:
            static_cars.append(static_car)

        # car is dependent on another
        reference_car, dependent_car, dependent_offset = parse_fixed_offset(a)

        if reference_car and dependent_car and dependent_offset:
            dependent_car_names.append(dependent_car)

            if reference_car not in dependent_cars.keys():
                dependent_cars[reference_car] = []
            dependent_cars[reference_car].append((dependent_car, dependent_offset))

        # car has a fixed movement
        fixed_movement_car, self_offsets = parse_fixed_movement(a, a_fml)

        if fixed_movement_car and self_offsets:
            fixed_movement_car_names.append(fixed_movement_car)

            if fixed_movement_car not in fixed_movement_cars.keys():
                fixed_movement_cars[fixed_movement_car] = []
            fixed_movement_cars[fixed_movement_car].extend(self_offsets)

    # independent_cars = set(nominals).difference(set(static_cars).union(set(dependent_car_names)).union(set(fixed_movement_car_names)))

    return static_cars, dependent_cars, fixed_movement_cars


def build_adjacency(dependencies):
    adjaceny_graph = {}
    for parent, children in dependencies.items():
        adjaceny_graph.setdefault(parent, [])
        for child, (dx, dy) in children:
            adjaceny_graph.setdefault(child, [])
            adjaceny_graph[parent].append((child, (dx, dy)))
            adjaceny_graph[child].append((parent, (-dx, -dy)))
    return adjaceny_graph


def compute_components(adjacency_graph):
    components = []
    visited = set()

    for start in adjacency_graph.keys():
        if start in visited:
            continue

        relative_pos = {start: (0, 0)}
        stack = [start]
        ok = True

        while stack and ok:
            node = stack.pop()
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
            return None  # inconsistent system -> no grids at all

        components.append(relative_pos)
        visited.update(relative_pos.keys())

    return components


def placements_for_component(rel_pos, grid_x, grid_y):
    xs = [x for (x, _) in rel_pos.values()]
    ys = [y for (_, y) in rel_pos.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    tx_min = -min_x
    tx_max = (grid_x - 1) - max_x
    ty_min = -min_y
    ty_max = (grid_y - 1) - max_y

    placements = []
    for tx in range(tx_min, tx_max + 1):
        for ty in range(ty_min, ty_max + 1):
            placement = {
                car: (x + tx, y + ty) for car, (x, y) in rel_pos.items()
            }
            placements.append(placement)
    return placements


def generate_grids(grid_size, propositions, nominals, components):
    constrained_cars = set()
    for comp in components:
        constrained_cars.update(comp.keys())

    if components is None:
        raise Exception("The given dependency formulas create a contradiction")

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

                    yield grid


def generate_traces(grid_size, propositions, nominals, static_cars, dependent_cars, fixed_movement_cars, trace_length):
    # build dependency graph between dependent cars
    adj = build_adjacency(dependent_cars)

    # dependent components in the dependency graph with relative positions
    components = compute_components(adj)

    if components is None:
        return []

    dep_cars = [x for xs in components for x in xs.keys()]

    independent_cars = set(nominals) - set(static_cars) - set(dep_cars) - set(fixed_movement_cars)

    for grid in generate_grids(grid_size, propositions, nominals, components):
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
                                    fixed_movement_cars, independent_cars, 1, trace_length, grid, [grid])


def check_in_bound(grid_size, point):
    return 0 <= point[0] < grid_size[0] and 0 <= point[1] < grid_size[1]


def add(p, d):
    return (p[0] + d[0], p[1] + d[1])


def combine_placements(grid_size, curr_grid, static_car_names, components, fixed_movement_car_names,
                       independent_car_names, moves, propositions):
    # this is ok
    static_car_moves = []
    for c in static_car_names:
        allowed_moves = [add(curr_grid[c], m) for m in moves[c] if check_in_bound(grid_size, add(curr_grid[c], m))]
        static_car_moves.append(allowed_moves)
    static_car_placements = product(*static_car_moves)

    # this is OK
    dep_cars = [x for xs in components for x in xs.keys()]
    fixed_car_moves = []
    for c in (set(fixed_movement_car_names) - set(dep_cars)):
        allowed_moves = [add(curr_grid[c], m) for m in moves[c] if check_in_bound(grid_size, add(curr_grid[c], m))]
        fixed_car_moves.append(allowed_moves)
    fixed_car_placements = product(*fixed_car_moves)
    # this is OK
    independent_car_moves = []
    for c in independent_car_names:
        allowed_moves = [add(curr_grid[c], m) for m in moves[c] if check_in_bound(grid_size, add(curr_grid[c], m))]
        independent_car_moves.append(allowed_moves)
    independent_car_placements = product(*independent_car_moves)

    # this is ok
    points: list[tuple[int, int]] = [(i, j) for i in range(grid_size[0]) for j in
                                     range(grid_size[1])]
    prop_placements: list[list] = [list(powerset(points)) for _ in propositions]

    dependent_components_placements = [[] for _ in components]
    for j in range(0, len(components)):
        members = list(components[j].keys())

        for mov in moves[members[0]]:
            all_in_grid = True
            pos = []
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

    for static_car_choice in product(*static_car_moves): #static_car_placements:
        for fixed_car_choice in product(*fixed_car_moves): #fixed_car_placements:
            for independent_car_choice in product(*independent_car_moves): #independent_car_placements:
                for dependent_component_choice in dependent_components_choices:
                    for prop_choice in product(*prop_placements):
                        placement = {}

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
                        yield placement    


def extend_trace(grid_size, propositions, static_cars, dependent_cars, components, fixed_movement_cars,
                 independent_cars, curr_trace_length, max_trace_length, prev_grid, trace):
    if curr_trace_length <= max_trace_length:
        yield trace
        if curr_trace_length == max_trace_length:
            return

    moves = {}

    # static cars are placed in the same position in the next time instance
    for s in static_cars:
        moves[s] = [(0, 0)]

    # all possible movements within grid bounds
    all_deltas = [
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
            fixed_movement_cars_in_c = list(set(c.keys()).intersection(set(fixed_movement_cars.keys())))

            # if entries exist but no common relative movements - discard movement
            if len(fixed_movement_cars_in_c) > 0:
                allowed_moves = fixed_movement_cars[fixed_movement_cars_in_c[0]]

                for i in range(1, len(fixed_movement_cars_in_c)):
                    allowed_moves = set(allowed_moves).intersection(set(fixed_movement_cars_in_c[i]))

                for car in c.keys():
                    moves[car] = allowed_moves

            else:
                # if no entries in fixed movement - all movements are possible
                for car in c.keys():
                    moves[car] = all_deltas

    # place fixed movement cars
    dep_cars = [x for xs in components for x in xs.keys()]
    for c in set(fixed_movement_cars) - set(dep_cars):
        moves[c] = fixed_movement_cars[c]

    # place independent cars
    for c in independent_cars:
        moves[c] = all_deltas

    # combine placements
    for placement in combine_placements(grid_size, prev_grid, static_cars, components, fixed_movement_cars.keys(),
                                        independent_cars, moves, propositions):
        yield from extend_trace(grid_size, propositions, static_cars, dependent_cars, components, fixed_movement_cars,
                                independent_cars, curr_trace_length + 1, max_trace_length, placement,
                                trace + [placement])


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
            if formula.evaluate(trace, (i, j), grid_size):
                points.append((i, j))

    return points


def evaluate(propositions: list[str], nominals: list[str], assumptions, conclusions, grid_size: tuple[int, int],
             max_trace_length: int,
             show_traces: bool):
    static_cars, dependent_cars, fixed_movement_cars = divide_cars_in_types(assumptions, nominals)

    # conjunction of assumptions and conclusion
    input_formula_string: str = "&".join([*("(" + x + ")" for x in conclusions),
                                          *("(" + x + ")" for x in assumptions)])

    # parse the input formula
    parsed_formula: HybridSpatioTemporalFormula = HybridSpatioTemporalParser(tokenize(input_formula_string)).parse()

    counter_sat = 0
    counter_gen = 0
    for t in generate_traces(grid_size, propositions, nominals, static_cars, dependent_cars, fixed_movement_cars,
                             max_trace_length):
        sat_points = satisfying_points(parsed_formula, t, grid_size)

        if sat_points:
            if show_traces:
                print("\t |Satisfying trace #", counter_sat, " with satisfying points: ", sat_points)
                print("\t |--------------------------------------------------------------------")
                print("\t |", t, "\n")
            counter_sat = counter_sat + 1
        counter_gen = counter_gen + 1
    print("|A total of ", counter_gen, " generated.")
    print("|A total of ", counter_sat, " satisfying traces found.")


if __name__ == '__main__':
    # list of propositions
    propositions = []

    # list of nominals
    nominals = ["z", "z1", "z2"]

    # list of assumptions (restrict the traces and points of interest)
    assumptions: list[str] = ["@z1 (↓z (G (@z1 (z))))", "G (@z2 ↓z X @z2 (Front z))"]

    # list of conclusions (formulas to be checked at all traces and spatial
    # points in which the assumptions hold)
    conclusions: list[str] = ["↓z1 F(z1 & z2)"]

    # size of the spatial grid graph (n x m)
    grid_size: tuple[int, int] = (3, 3)

    evaluate(propositions, nominals, assumptions, conclusions, grid_size, 2, True)
