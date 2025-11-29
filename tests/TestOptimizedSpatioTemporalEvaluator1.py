import unittest
from checkers.optimized_version.evaluator_optimized.SpatioTemporalEvaluator1 import satisfying_points, generate_traces, \
    generate_all_satisfying_grids
from formula_types.ClassicalLogicFormula import And, Not
from formula_types.HybridFormula import Nom, Bind, At
from formula_types.SpatialFormula import Front, Left
from formula_types.TemporalFormula import Eventually, Always


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
            2 == len(generate_all_satisfying_grids([], ["z1", "z2"], self.grid_size, [always_at_z1_left_z2])))

    def test_generate_all_satisfying_grids2(self):
        self.assertTrue(16 == len(generate_all_satisfying_grids([], ["z1", "z2"], self.grid_size, [])))

    def test_generate_traces1(self):
        self.assertTrue(16 * 4 == len(list(generate_traces(["a"], ["z1"], self.grid_size, 1, []))))

    def test_generate_traces2(self):
        always_at_z1_left_z2 = Always("ALWAYS", At("z1", "AT", Left("LEFT", self.z2)))
        self.assertTrue(6 == len(list(generate_traces([], ["z1", "z2"], self.grid_size, 2, [always_at_z1_left_z2]))))


if __name__ == '__main__':
    unittest.main()
