from parsers.SpatialFormulaParser import tokenize, SpatialParser
from itertools import combinations
from itertools import product


def generate_grids(grid_size, car_propositions):
    nr_positions = grid_size[0]*grid_size[1]
    grids = list()

    for choices in product(range(nr_positions + 1), repeat=len(car_propositions)):
        cells = [set() for _ in range(nr_positions)]

        for s, t in zip(car_propositions, choices):
            if t < nr_positions:
                cells[t].add(s)
        grids.append([[list(cells[r*grid_size[1] + c]) for c in range(grid_size[1])] for r in range(grid_size[0])])
    return grids


def evaluate_assignment(formula, assigned_grid):
    for i in range(0, len(assigned_grid)):
        for j in range(0, len(assigned_grid[i])):
            if not formula.evaluate([assigned_grid], (i, j)):
                return False
    return True


def evaluate_validity(formula, grid_size, car_propositions):
    assigned_grids = generate_grids(grid_size, car_propositions)

    for assigned_grid in assigned_grids:
        if not evaluate_assignment(formula, assigned_grid):
            print(assigned_grid)
            return False

    return True

if __name__ == '__main__':
    PROPOSITIONS = ['sv', 'pov1']
    INPUT_FORMULA = "(!(Left(sv) <-> ⊥)) -> (Left(Right(sv)) <-> Right(Left(sv)))"

    # GRID IS GRID_SIZE X GRID_SIZE
    GRID_SIZE = (3,3)
    GRID = [
        [[], [], []],
        [[], ['sv', 'pov1'], []],
        [[], ['pov1'], []]
    ]

    parsed_formula = SpatialParser(tokenize(INPUT_FORMULA)).parse()
    print(parsed_formula)
    print(evaluate_validity(parsed_formula, GRID_SIZE, PROPOSITIONS))



