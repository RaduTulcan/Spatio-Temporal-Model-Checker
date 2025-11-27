import unittest

from formula_types.ClassicalLogicFormula import Prop
from formula_types.TemporalFormula import Next, Always, Eventually, Until

class TestTemporalFormula(unittest.TestCase):
    def setUp(self):
        self.point1 = (0,0)
        self.point2 = (0,1)
        self.point3 = (1,0)
        self.point4 = (1,1)

        self.grid_size = (2,2)

        self.trace = [
            {
                'a' : [self.point1],
                'b' : [],
                'c' : [self.point1],
                'd' : [],
            }
        ] * 9 + [
            {
                'a' : [],
                'b' : [self.point1],
                'c' : [self.point1],
                'd' : [],
            }
        ]

    def test_next_evaluate(self):
        pass

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

    def test_complex_formula1_evaluate(self):
        pass

    def test_complex_formula2_evaluate(self):
        pass

if __name__ == '__main__':
    unittest.main()
