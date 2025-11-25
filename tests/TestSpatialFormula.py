import unittest

from formula_types.HybridFormula import Nom


class TestSpatialFormula(unittest.TestCase):

    def setUp(self):
        self.point1 = (0, 0)
        self.point2 = (0, 1)
        self.point3 = (1, 0)
        self.point4 = (1, 1)

        self.grid = [{
            'z1': self.point1,
            'z2': self.point2
        }]

        self.z1 = Nom("z1")
        self.z2 = Nom("z2")

    def test_left_evaluate(self):
        pass

    def test_right_evaluate(self):
        pass

    def test_front_evaluate(self):
        pass

    def test_back_evaluate(self):
        pass

    def test_evaluate_validities_inside_bounds(self):
        pass


if __name__ == '__main__':
    unittest.main()
