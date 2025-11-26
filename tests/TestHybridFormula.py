import unittest

from formula_types.ClassicalLogicFormula import Not, And, If, Iff
from formula_types.HybridFormula import Nom, At, Bind


class TestHybridFormula(unittest.TestCase):
    def setUp(self):
        self.point1 = (0, 0)
        self.point2 = (0, 1)
        self.point3 = (1, 0)
        self.point4 = (1, 1)

        self.grid_size = (2,2)

        self.grid = [{
            'z1': self.point1,
            'z2': self.point2
        }]

        self.z1 = Nom("z1")
        self.z2 = Nom("z2")

    def test_nominal_evaluate(self):
        self.assertTrue(self.z1.evaluate(self.grid, self.point1, self.grid_size))
        self.assertFalse(self.z2.evaluate(self.grid, self.point3, self.grid_size))

    def test_nominal_evaluate_out_of_bounds(self):
        self.assertFalse(self.z1.evaluate(self.grid, (-1, -1), self.grid_size))

    def test_at_evaluate(self):
        at_z1_z2 = At("z1", "AT", self.z2)
        at_z1_not_z2 = At("z1", "AT", Not("NOT", self.z2))

        for pt in [self.point1, self.point2, self.point3, self.point4]:
            self.assertFalse(at_z1_z2.evaluate(self.grid, pt, self.grid_size))
            self.assertTrue(at_z1_not_z2.evaluate(self.grid, pt, self.grid_size))

    def test_bind_evaluate(self):
        bind_z1_z1_and_z2 = Bind("z1", ":z1", And("AND", self.z1, self.z2))

        self.assertTrue(bind_z1_z1_and_z2.evaluate(self.grid, self.point2, self.grid_size))
        self.assertFalse(bind_z1_z1_and_z2.evaluate(self.grid, self.point3, self.grid_size))

    def test_evaluate_validities(self):
        at_z1_z1 = At("z1", "AT", self.z1)
        at_z1_z2_implies_at_z2_z1 = If("IMPLIES", At("z1", "AT", self.z2), At("z2", "AT", self.z1))
        bind_z1_z1 = Bind("z1", "BIND", self.z1)
        bind_z1_z1_and_z2_iff_bind_z1_at_z1_z1_and_z2 = Iff("IFF", Bind("z1", "BIND", And("AND", self.z1, self.z2)),
                                                            Bind("z1", "BIND",
                                                                 At("z1", "AT", And("AND", self.z1, self.z2))))

        for pt in [self.point1, self.point2, self.point3, self.point4]:
            self.assertTrue(at_z1_z1.evaluate(self.grid, pt, self.grid_size))
            self.assertTrue(at_z1_z2_implies_at_z2_z1.evaluate(self.grid, pt, self.grid_size))
            self.assertTrue(bind_z1_z1.evaluate(self.grid, pt, self.grid_size))
            self.assertTrue(bind_z1_z1_and_z2_iff_bind_z1_at_z1_z1_and_z2.evaluate(self.grid, pt, self.grid_size))


if __name__ == '__main__':
    unittest.main()
