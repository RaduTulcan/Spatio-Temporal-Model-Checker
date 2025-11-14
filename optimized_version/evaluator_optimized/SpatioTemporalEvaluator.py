from optimized_version.parsers_optimized.HybridSpatioTemporalFormulaParser import HybridSpatioTemporalParser, tokenize
from itertools import chain, combinations, product


def powerset(iterable):
    """Return all subsets of iterable as tuples."""
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def generate_all_satisfying_starting_states(size_of_bounding_box, propositions, nominals, assumptions, conclusion):
    """
        This function generate all possible starting states in the grid.
        (Since any position can be a starting point for any car, it generates all possible placements)
    """

    # generate all points found in the bounding box
    points = [(i, j) for i in range(size_of_bounding_box[0]) for j in range(size_of_bounding_box[1])]

    # generate all possible placements for each proposition
    prop_placements = [list(powerset(points)) for _ in propositions]

    nominal_placements = [points for _ in nominals]

    # iterate over all possible placements of atomic components
    for prop_choice in product(*prop_placements):
        for nominal_choice in product(*nominal_placements):
            placement = {}

            # Add propositions with their chosen subsets
            for name, subset in zip(propositions, prop_choice):
                placement[name] = list(subset)

            # Add nominals with their single chosen point (wrapped in a list)
            for name, pos in zip(nominals, nominal_choice):
                placement[name] = pos

            # check whether in the generated state, the assumptions hold
            assumptions_hold = True
            for assumption in assumptions:
                for p in points:
                    if not assumption.evaluate([placement], p):
                        assumptions_hold = False
                        break

                if not assumptions_hold:
                    break

            # consider these states, only if the assumption holds
            if assumptions_hold:
                yield placement


if __name__ == '__main__':
    PROPOSITIONS = ['a', 'b']
    NOMINALS = ['z']
    ASSUMPTIONS = ['G @z(a)', 'a -> Front(b)']
    CONCLUSION = ['a']
    SIZE_OF_BOUNDING_BOX = (3,3)

    if len(set(PROPOSITIONS).intersection(set(NOMINALS))) != 0:
        raise Exception("The sets of propositions and nominals must be disjoint.")

    if len(CONCLUSION) == 0:
        raise Exception("Conclusion cannot be empty.")

    parsed_assumptions = [HybridSpatioTemporalParser(tokenize(assumption)).parse() for assumption in ASSUMPTIONS]
    parsed_conclusion = [HybridSpatioTemporalParser(tokenize(conclusion)).parse() for conclusion in CONCLUSION]

    #TODO: filter out assumptions that contain X, U, F (cannot be evaluated at a single grid); G, hybrid and classical operators can
    allowed_states = list(generate_all_satisfying_starting_states(SIZE_OF_BOUNDING_BOX, PROPOSITIONS, NOMINALS, parsed_assumptions, parsed_conclusion))
    print(allowed_states)


