import unittest

from formula_types.ClassicalLogicFormula import Prop, Not, And, If, Iff
from formula_types.SpatialFormula import Left, Right, Front, Back
from formula_types.TemporalFormula import Eventually, Always, Until
from formula_types.HybridFormula import Nom, At, Bind


class TestHybridSpatioTemporalFormula(unittest.TestCase):
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

    def test_validities_evaluet(self):
        for p1 in ['a', 'b', 'c', 'd']:
            for p2 in ['a', 'b', 'c', 'd']:
                prop1 = Prop(p1)
                prop2 = Prop(p2)
                left_until = Left("LEFT", Until("UNTIL", prop1, prop2))
                until_left = Until("UNTIL", Left("LEFT", prop1), Left("LEFT", prop2))
                for pt in [self.point1, self.point2, self.point3, self.point4]:
                    self.assertTrue(Iff("IFF", left_until, until_left).evaluate(self.trace, pt, self.grid_size))

    def test_complex_formula1_evaluate(self):
        pass

    def test_complex_formula2_evaluate(self):
        pass


if __name__ == '__main__':
    unittest.main()
