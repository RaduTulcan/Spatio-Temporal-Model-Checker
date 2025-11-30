import unittest
from checkers.optimized_version.evaluator_optimized.OptimizedSpatioTemporalEvaluator2 import satisfying_points, generate_traces, generate_grids, divide_cars_in_types, filter_state_assumptions, build_adjacency, compute_components, divide_cars_in_types
from parsers.HybridSpatioTemporalFormulaParser import HybridSpatioTemporalParser, tokenize
from formula_types.ClassicalLogicFormula import And, Not
from formula_types.HybridFormula import Nom, Bind, At
from formula_types.SpatialFormula import Front, Left
from formula_types.TemporalFormula import Eventually, Always
from pprint import pprint as pp


class TestOptimizedSpatioTemporalEvaluator1(unittest.TestCase):

    def setUp(self):
        self.point1 = (0, 0)
        self.point2 = (0, 1)
        self.point3 = (1, 0)
        self.point4 = (1, 1)

        self.grid_size = (2, 2)

        self.trace = [
            {'z1': self.point3, 'z2': self.point4},
            {'z1': self.point2, 'z2': self.point2}
        ]

        self.z1 = Nom("z1")
        self.z2 = Nom("z2")

    def test_no_satisfying_points(self):
        z1_and_z2 = And("AND", self.z1, self.z2)
        self.assertTrue([] == satisfying_points(z1_and_z2, self.trace, self.grid_size))

    def test_some_satisfying_points1(self):
        f_z1_and_z2 = Eventually("EVENTUALLY", And("AND", self.z1, self.z2))
        self.assertTrue([self.point2] == satisfying_points(f_z1_and_z2, self.trace, self.grid_size))

    def test_generate_all_satisfying_grids1(self):
        always_at_z1_left_z2 = Always("ALWAYS", At("z1", "AT", Left("LEFT", self.z2)))
        self.assertTrue(
            2 == len(list(generate_grids(self.grid_size, [], ["z1", "z2"], [], [always_at_z1_left_z2]))))

    def test_generate_all_satisfying_grids2(self):
        self.assertTrue(16 == len(list(generate_grids(self.grid_size, [], ["z1", "z2"], [], []))))

    def test_generate_grids3(self):
        z1_fixed = "@z1 ↓z0 (G @z1 (z0))"
        z2_behind_z3 = "G @z2 Front z3"
        a_until_b = "G (a | b)"
        assumptions = [z1_fixed, z2_behind_z3, a_until_b]
        static_cars, dependent_cars, fixed_movement_cars, remaining_assumptions = divide_cars_in_types(assumptions, ['z1', 'z2', 'z3'])
        adj = build_adjacency(dependent_cars)
        components = compute_components(adj)
        parsed_state_assumptions = [HybridSpatioTemporalParser(tokenize(fml)).parse() for fml in remaining_assumptions]
        grids = list(generate_grids(self.grid_size, ['a', 'b'], ['z1', 'z2', 'z3'], components, parsed_state_assumptions))
        # print(len(grids))
        self.assertTrue(True)

    def test_generate_traces1(self):
        self.assertTrue(16 * 4 == len(list(generate_traces(self.grid_size, ["a"], ["z1"], [], {}, {}, [], 1))))

    def test_generate_traces2(self):
        always_at_z1_left_z2 = Always("ALWAYS", At("z1", "AT", Left("LEFT", self.z2)))
        traces = list(generate_traces(self.grid_size, [], ["z1", "z2"], [], {}, {}, [always_at_z1_left_z2], 2))
        self.assertTrue(6 == len(traces))


    def test_generate_traces3(self):
        z1_fixed = "@z1 ↓z0 (G @z1 (z0))"
        z2_behind_z3 = "G @z2 Front z3"
        a_or_b = "G (a | b)"
        assumptions1 = [z1_fixed, z2_behind_z3, a_or_b]
        nominals = ["z1", "z2", "z3"]

        static_cars, dependent_cars, fixed_movement_cars, remaining_assumptions1 = divide_cars_in_types(assumptions1, nominals)
        state_assumptions, remaining_assumptions1 = filter_state_assumptions(remaining_assumptions1)
        parsed_state_assumptions1 = [HybridSpatioTemporalParser(tokenize(fml)).parse() for fml in state_assumptions]


        self.assertTrue(4*2 + 4*4 == len(list(generate_traces(self.grid_size, [], nominals, static_cars, dependent_cars, fixed_movement_cars, [], 2))))

        self.assertTrue((3**4)*4*2 + (3**4)**2 * 4*4 == len(list(generate_traces(self.grid_size, ['a', 'b'], nominals, static_cars, dependent_cars, fixed_movement_cars, parsed_state_assumptions1, 2))))


if __name__ == '__main__':
    unittest.main()
