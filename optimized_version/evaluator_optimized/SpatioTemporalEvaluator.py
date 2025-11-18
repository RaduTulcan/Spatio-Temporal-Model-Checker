# TODO
# 1) scan over all formulas and select the important ones [DONE]
# 2) parse all the formulas as usual []
# 3) extract car position information about the formulas of interest [DONE]
# 4) generate grids according to the positional information (type (2) formulas) []\
#   - check if different cars can be placed at different positions
# 5) generate traces according to positional information []
import re
from itertools import chain, combinations, product

DIRECTIONS = {
    "Left":  (0, -1),
    "Right": (0,  1),
    "Front": (-1, 0),
    "Back":  (1, 0),
}


def tokenize(formula: str):
    spaced = formula.replace("(", " ( ").replace(")", " ) ")
    return [t for t in spaced.split() if t]


def strip_parentheses(tokens):
    return [t for t in tokens if t not in ("(", ")")]


def parse_static_car(formula: str):
    tokens = strip_parentheses(tokenize(formula))

    # formula has exactly 5 tokens (without parentheses)
    if len(tokens) != 5:
        return None

    # binder syntax must match
    if not re.fullmatch(r"↓z[0-9_]*", tokens[1]):
        return None

    # at syntax must match
    if not re.fullmatch(r"@z[0-9_]*", tokens[0]):
        return None

    # globally operator must exist
    if tokens[2] != "G":
        return None

    # binder nominal must match the last token
    if tokens[1][1:] != tokens[4]:
        return None

    # both @-occurrences must match
    if tokens[0] != tokens[3]:
        return None

    return tokens[0][1:]


def dirs_to_offset(dirs):
    x = y = 0
    for d in dirs:
        dx, dy = DIRECTIONS[d]
        x += dx
        y += dy
    return x, y


def parse_fixed_offset(formula: str):
    tokens = strip_parentheses(tokenize(formula))

    if tokens[0] != "G":
        return None, None, None

    if not re.fullmatch(r"@z[0-9_]*", tokens[1]):
        return None, None, None

    if not re.fullmatch(r"z[0-9_]*", tokens[-1]):
        return None, None, None

    directions = tokens[2:-1]

    # check that all other tokens are only directions
    if len(directions) == 0:
        return None, None, None

    for d in directions:
        if d != "Left" and d != "Right" and d != "Back" and d != "Front":
            return None, None, None

    reference_car = tokens[1][1:]
    dependent_car = tokens[-1]
    offset = dirs_to_offset(directions)
    return reference_car, dependent_car, offset


def parse_fixed_movement(formula):
    branches = [b.strip() for b in formula.split("|")]
    offsets = []
    first_branch = branches[0]
    tokens_first = tokenize(first_branch)

    # formula must start with globally operator
    if tokens_first[0] != "G":
        return None, None

    # followed by at-operator and a nominal
    if not re.fullmatch(r"@z[0-9_]*", tokens_first[1]):
        return None, None

    # followed by a binding operator
    if not re.fullmatch(r"↓z[0-9_]*", tokens_first[2]):
        return None, None

    # followed by next operator
    if tokens_first[3] != "X":
        return None, None

    # the nominals for at-operator must match
    if tokens_first[1] != tokens_first[4]:
        return None, None

    # "free" nominals used after the binding operator must match the nominial of the operator
    if tokens_first[-1] != tokens_first[2][1:]:
        return None, None

    car = tokens_first[1][1:]
    directions = tokens_first[5:-1]

    # check that all other tokens are only directions
    if len(directions) == 0:
        return None, None

    for d in directions:
        if d != "Left" and d != "Right" and d != "Back" and d != "Front":
            return None, None

    offsets.append(dirs_to_offset(directions))

    for b in branches[1:]:
        tok = tokenize(b)
        directions = tok[:-1]

        # "free" nominals used after the binding operator must match the nominial of the operator
        if tok[-1] != tokens_first[2][1:]:
            return None, None

        for d in directions:
            if d != "Left" and d != "Right" and d != "Back" and d != "Front":
                return None, None

        offsets.append(dirs_to_offset(directions))

    return car, offsets


def divide_cars_in_types(assumptions, nominals):
    static_cars = []
    dependent_cars = {}
    fixed_movement_cars = {}
    dependent_car_names = []
    fixed_movement_car_names = []

    for a in assumptions:
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
        fixed_movement_car, self_offsets = parse_fixed_movement(a)

        if fixed_movement_car and self_offsets:
            fixed_movement_car_names.append(fixed_movement_car)

            if fixed_movement_car not in fixed_movement_cars.keys():
                fixed_movement_cars[fixed_movement_car] = []
            fixed_movement_cars[fixed_movement_car].extend(self_offsets)

    # independent_cars = set(nominals).difference(set(static_cars).union(set(dependent_car_names)).union(set(fixed_movement_car_names)))

    return static_cars, dependent_cars, fixed_movement_cars


def powerset(iterable):
    """Return all subsets of iterable as tuples."""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


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


def generate_grids(grid_size, propositions, dependent_cars, nominals):

    # build dependency graph between dependent cars
    adj = build_adjacency(dependent_cars)

    # dependent components in the dependency graph with relative positions
    components = compute_components(adj)

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

    print(component_placements)

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




if __name__ == '__main__':
    # list of propositions
    propositions = ["a"]

    # list of nominals
    nominals = ["z", "z2", "z1", "z3", "z4"]

    # list of assumptions (restrict the traces and points of interest)
    assumptions: list[str] = ["@z1 (↓z (G (@z1 (z))))", "G @z1 Left (Left z2)", "G @z4 Left (z3)", "G @z3 ↓z X @z3 Left z | Right z | Front Front z"]

    # list of conclusions (formulas to be checked at all traces and spatial
    # points in which the assumptions hold)
    conclusions: list[str] = ["↓z F(z & z2)"]

    # size of the spatial grid graph (n x m)
    grid_size: tuple[int, int] = (3, 3)

    static_cars, dependent_cars, fixed_movement_cars = divide_cars_in_types(assumptions, nominals)

    for grid in generate_grids(grid_size, propositions, dependent_cars, nominals):
        print(grid)



