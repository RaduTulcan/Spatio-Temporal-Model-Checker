import unittest
from checkers.baseline_version.evaluator_baseline.BaselineSpatioTemporalEvaluator import generate_trace_from_spec, \
    satisfying_points, generate_traces
from formula_types.ClassicalLogicFormula import And, Not, Prop
from formula_types.HybridFormula import Nom, Bind
from formula_types.SpatialFormula import Front
from formula_types.TemporalFormula import Eventually, Always


class TestBaselineSpatioTemporalEvaluator(unittest.TestCase):

    def setUp(self):
        self.point1 = (0, 0)
        self.point2 = (0, 1)
        self.point3 = (1, 0)
        self.point4 = (1, 1)

        self.grid_size = (2,2)

        self.trace = [
            {'z1': self.point3, 'z2': self.point4},
            {'z1': self.point2, 'z2': self.point2}
        ]

        self.z1 = Nom("z1")
        self.z2 = Nom("z2")

    def test_generate_traces_from_spec(self):
        trace_spec = [
            [";;", "z;z;z2,z", ";;"],
            [";;", ";z2;", ";;"],
            [";;", "z3,z2;z3;z3", ";;"]
        ]

        correct_result = [
            {"z": (0, 1), "z2": (2, 1), "z3": (2, 1)},
            {"z": (0, 1), "z2": (1, 1), "z3": (2, 1)},
            {"z": (0, 1), "z2": (0, 1), "z3": (2, 1)},
        ]

        self.assertTrue(correct_result == generate_trace_from_spec(trace_spec, (len(trace_spec), len(trace_spec[0]))))

    def test_generate_traces_from_spec_with_propositions(self):
        trace_spec = [
            ["a;;", "z;z;z2,z", ";;a,b"],
            ["a;;", ";z2,b;", ";b;"],
            [";;", "z3,z2;z3;z3", ";;"]
        ]

        correct_result = [
            {"z": (0, 1), "z2": (2, 1), "z3": (2, 1), "a": [(0,0), (1,0)]},
            {"z": (0, 1), "z2": (1, 1), "z3": (2, 1), "b": [(1,1), (1,2)]},
            {"z": (0, 1), "z2": (0, 1), "z3": (2, 1), "a": [(0,2)], "b": [(0,2)]},
        ]
        print(generate_trace_from_spec(trace_spec, (len(trace_spec), len(trace_spec[0]))))
        self.assertTrue(correct_result == generate_trace_from_spec(trace_spec, (len(trace_spec), len(trace_spec[0]))))

    def test_no_satisfying_points(self):
        z1_and_z2 = And("AND", self.z1, self.z2)
        self.assertTrue([] == satisfying_points(z1_and_z2, self.trace,self.grid_size))

    def test_some_satisfying_points1(self):
        f_z1_and_z2 = Eventually("EVENTUALLY", And("AND", self.z1, self.z2))
        self.assertTrue([self.point2] == satisfying_points(f_z1_and_z2, self.trace, self.grid_size))

    def test_some_satisfying_points2(self):
        g_not_z1 = Always("ALWAYS", Not("NOT", self.z1))
        self.assertTrue([self.point1, self.point4] == satisfying_points(g_not_z1, self.trace, self.grid_size))

    def test_some_satisfying_points3(self):
        at_z2_font_f_z1 = Bind("z2", "BIND", Front("FRONT", Eventually("EVENTUALLY", self.z1)))
        self.assertTrue([self.point4] == satisfying_points(at_z2_font_f_z1, self.trace, self.grid_size))

    def test_generate_traces1(self):
        self.assertTrue([{"z1": (0, 0)}] in list(generate_traces([], ["z1"], 1, self.grid_size)))
        self.assertTrue([{"z1": (0, 1)}] in list(generate_traces([], ["z1"], 1, self.grid_size)))
        self.assertTrue([{"z1": (1, 0)}] in list(generate_traces([], ["z1"], 1, self.grid_size)))
        self.assertTrue([{"z1": (1, 1)}] in list(generate_traces([], ["z1"], 1, self.grid_size)))

    def test_generate_traces2(self):
        self.assertTrue(16 * 4 == len(list(generate_traces(["a"], ["z1"], 1, self.grid_size))))

    def test_generate_traces3(self):
        self.assertTrue((16 * 4) + (16*16 * 4*4) == len(list(generate_traces(["a"], ["z1"], 2, self.grid_size))))


if __name__ == '__main__':
    unittest.main()
