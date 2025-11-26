import unittest

from formula_types.ClassicalLogicFormula import Iff, Verum, If
from formula_types.HybridFormula import Nom
from formula_types.SpatialFormula import Left, Right, Front, Back


class TestSpatialFormula(unittest.TestCase):

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

    def test_left_evaluate(self):
        left_z1 = Left("LEFT", self.z1)
        self.assertFalse(left_z1.evaluate(self.grid, self.point1, self.grid_size))
        self.assertTrue(left_z1.evaluate(self.grid, self.point2, self.grid_size))

    def test_right_evaluate(self):
        right_z2 = Right("RIGHT", self.z2)
        self.assertFalse(right_z2.evaluate(self.grid, self.point2, self.grid_size))
        self.assertTrue(right_z2.evaluate(self.grid, self.point1, self.grid_size))

    def test_front_evaluate(self):
        front_z1 = Front("FRONT", self.z1)
        self.assertFalse(front_z1.evaluate(self.grid, self.point1, self.grid_size))
        self.assertTrue(front_z1.evaluate(self.grid, self.point3, self.grid_size))

    def test_back_evaluate(self):
        back_z2 = Back("BACK", self.z2)
        back_true = Back("BACK", Verum())
        self.assertTrue(back_z2.evaluate(self.grid, (-1,1), self.grid_size))
        self.assertFalse(back_z2.evaluate(self.grid, self.point2, self.grid_size))
        self.assertFalse(back_true.evaluate(self.grid, self.point4, self.grid_size))

    def test_evaluate_validities(self):
        validity1 = Iff("IFF", Front("FRONT", Right("RIGHT", self.z1)), Right("RIGHT", Front("FRONT", self.z1)))
        validity2 = Iff("IFF", Front("FRONT", Left("LEFT", self.z1)), Left("LEFT", Front("FRONT", self.z1)))
        validity3 = Iff("IFF", Back("BACK", Right("RIGHT", self.z1)), Right("RIGHT", Back("BACK", self.z1)))
        validity4 = Iff("IFF", Back("BACK", Left("LEFT", self.z1)), Left("LEFT", Back("BACK", self.z1)))
        validity5 = If("IMPLIES", Back("BACK", Right("RIGHT", Front("FRONT", Left("LEFT", self.z1)))), self.z1)
        for pt in [self.point1, self.point2, self.point3, self.point4]:
            self.assertTrue(validity1.evaluate(self.grid, pt, self.grid_size))
            self.assertTrue(validity2.evaluate(self.grid, pt, self.grid_size))
            self.assertTrue(validity3.evaluate(self.grid, pt, self.grid_size))
            self.assertTrue(validity4.evaluate(self.grid, pt, self.grid_size))
            self.assertTrue(validity5.evaluate(self.grid, pt, self.grid_size))

    def test_evaluate_exceed_bounds(self):
        left_right_z1 = Left("LEFT", Right("RIGHT", self.z1))
        self.assertFalse(left_right_z1.evaluate(self.grid, self.point1, self.grid_size))


if __name__ == '__main__':
    unittest.main()
