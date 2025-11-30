import unittest

from formula_types.ClassicalLogicFormula import Prop, Verum, Not, If
from formula_types.TemporalFormula import Next, Always, Eventually, Until


class TestTemporalFormula(unittest.TestCase):
    def setUp(self):
        self.point1 = (0, 0)
        self.point2 = (0, 1)
        self.point3 = (1, 0)
        self.point4 = (1, 1)

        self.grid_size = (2, 2)

        self.trace = [
                         {
                             'a': [self.point1],
                             'b': [],
                             'c': [self.point1],
                             'd': [],
                             'e': []
                         }
                     ] * 9 + [
                         {
                             'a': [],
                             'b': [self.point1],
                             'c': [self.point1],
                             'd': [],
                             'e': [self.point2],
                         }
                     ]

    def test_next_evaluate(self):
        next_top = Next("NEXT", Verum())
        self.assertFalse(next_top.evaluate(self.trace[-1:], self.point1, self.grid_size))
        self.assertTrue(next_top.evaluate(self.trace[-2:], self.point1, self.grid_size))

    def test_globally_evaluate(self):
        always_a = Always("ALWAYS", Prop("a"))
        self.assertFalse(always_a.evaluate(self.trace, self.point1, self.grid_size))
        self.assertTrue(always_a.evaluate(self.trace[:5], self.point1, self.grid_size))

    def test_eventually_evaluate(self):
        eventually_b = Eventually("EVENTUALLY", Prop("b"))
        self.assertTrue(eventually_b.evaluate(self.trace, self.point1, self.grid_size))
        self.assertFalse(eventually_b.evaluate(self.trace[:5], self.point1, self.grid_size))

    def test_until_evaluate(self):
        a_until_b = Until("UNTIL", Prop("a"), Prop("b"))
        c_until_d = Until("UNTIL", Prop("c"), Prop("d"))
        a_until_b_until_c_until_d = Until("UNTIL", a_until_b, c_until_d)
        self.assertTrue(a_until_b.evaluate(self.trace, self.point1, self.grid_size))
        self.assertFalse(c_until_d.evaluate(self.trace, self.point1, self.grid_size))
        self.assertFalse(a_until_b_until_c_until_d.evaluate(self.trace, self.point1, self.grid_size))

    def test_complex_formula_evaluate(self):
        not_a_implies_not_a_until_e = If("IMPLIES", Not("NOT", Prop("a")),
                                         Next("NEXT", Until("UNTIL", Not("NOT", Prop("a")), Prop("e"))))
        self.assertTrue(not_a_implies_not_a_until_e.evaluate(self.trace, self.point2, self.grid_size))

    def test_validity_evaluate(self):
        validity = If("IMPLIES", Until("UNTIL", Always("ALWAYS", Prop("a")), Eventually("EVENTUALLY", Prop("b"))),
                      Always("ALWAYS", Until("UNTIL", Prop("a"), Eventually("EVENTUALLY", Prop("b")))))
        for pt in [self.point1, self.point2, self.point3, self.point4]:
            self.assertTrue(validity.evaluate(self.trace, pt, self.grid_size))


if __name__ == '__main__':
    unittest.main()
