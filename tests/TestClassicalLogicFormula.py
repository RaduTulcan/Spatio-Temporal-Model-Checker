import unittest
from formula_types.ClassicalLogicFormula import Prop, Verum, Falsum, Not, And, Or, If, Iff


class TestClassicalLogicFormula(unittest.TestCase):

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)

    def setUp(self):
        self.point1 = (0,0)
        self.point2 = (0,1)
        self.point3 = (1,0)
        self.point4 = (1,1)

        self.grid_size = (2,2)

        self.grid = [{
            'a': [self.point1, self.point2],
            'b': [self.point1, self.point3, self.point4]
        }]

        self.a = Prop("a")
        self.b = Prop("b")

    def test_verum_evaluate_always_true(self):
        v = Verum()
        for pt in [self.point1, self.point2, self.point3, self.point4]:
            self.assertTrue(v.evaluate(self.grid, pt, self.grid_size))

    def test_falsum_evaluate_always_false(self):
        f = Falsum()
        for pt in [self.point1, self.point2, self.point3, self.point4]:
            self.assertFalse(f.evaluate(self.grid, pt, self.grid_size))

    def test_proposition_evaluate_when_at_point(self):
        self.assertTrue(self.a.evaluate(self.grid, self.point1, self.grid_size))
        self.assertTrue(self.b.evaluate(self.grid, self.point3, self.grid_size))

    def test_proposition_evaluate_when_not_at_point(self):
        self.assertFalse(self.a.evaluate(self.grid, self.point3, self.grid_size))
        self.assertFalse(self.b.evaluate(self.grid, self.point2, self.grid_size))

    def test_not_evaluate(self):
        not_a = Not("NOT", self.a)
        self.assertTrue(not_a.evaluate(self.grid, self.point3, self.grid_size))
        self.assertFalse(not_a.evaluate(self.grid, self.point1, self.grid_size))

    def test_and_evaluate(self):
        a_and_b = And("AND", self.a, self.b)
        self.assertTrue(a_and_b.evaluate(self.grid, self.point1, self.grid_size))
        self.assertFalse(a_and_b.evaluate(self.grid, self.point2, self.grid_size))

    def test_or_evaluate(self):
        a_or_b = Or("OR", self.a, self.b)

        for pt in [self.point1, self.point2, self.point3, self.point4]:
            self.assertTrue(a_or_b.evaluate(self.grid, pt, self.grid_size))

    def test_if_evaluate(self):
        a_implies_b = If("IMPLIES", self.a, self.b)

        self.assertTrue(a_implies_b.evaluate(self.grid, self.point3, self.grid_size))
        self.assertFalse(a_implies_b.evaluate(self.grid, self.point2, self.grid_size))

    def test_iff_evaluate(self):
        a_iff_b = Iff("IFF", self.a, self.b)

        self.assertTrue(a_iff_b.evaluate(self.grid, self.point1, self.grid_size))
        self.assertFalse(a_iff_b.evaluate(self.grid, self.point2, self.grid_size))

    def test_complex_formula_evaluate(self):
        # a -> b | (a & b)
        complex_formula = Or("OR", If("IMPLIES", self.a, self.b), And("AND", self.a, self.b))

        self.assertTrue(complex_formula.evaluate(self.grid, self.point1, self.grid_size))
        self.assertFalse(complex_formula.evaluate(self.grid, self.point2, self.grid_size))


if __name__ == '__main__':
    unittest.main()
