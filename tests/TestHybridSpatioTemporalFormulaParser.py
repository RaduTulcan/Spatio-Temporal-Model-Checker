import unittest
from parsers.HybridSpatioTemporalFormulaParser import tokenize, HybridSpatioTemporalParser


class TestHybridSpatioTemporalFormulaParser(unittest.TestCase):

    def test_parse_simple_classical_operators(self):
        self.assertTrue("¬ a" == str(HybridSpatioTemporalParser(tokenize("!a")).parse()))
        self.assertTrue("a ∧ b" == str(HybridSpatioTemporalParser(tokenize("a & b")).parse()))
        self.assertTrue("a | b" == str(HybridSpatioTemporalParser(tokenize("a | b")).parse()))
        self.assertTrue("a → b" == str(HybridSpatioTemporalParser(tokenize("a -> b")).parse()))
        self.assertTrue("a ↔ b" == str(HybridSpatioTemporalParser(tokenize("a <-> b")).parse()))

    def test_parse_nested_classical_operators(self):
        self.assertTrue("((¬ a) ∧ b) → (c | d)" == str(HybridSpatioTemporalParser(tokenize("(!a & b) -> (c | d)")).parse()))
        self.assertTrue(
            "(a ∧ b) ↔ ((c | d) ↔ (¬ d))" == str(HybridSpatioTemporalParser(tokenize("(a & b) <-> ((c | d) <-> !d)")).parse()))

    def test_parse_simple_hybrid_operators(self):
        self.assertTrue("@z1 z2" == str(HybridSpatioTemporalParser(tokenize("@z1 z2")).parse()))
        self.assertTrue("↓z1 z2" == str(HybridSpatioTemporalParser(tokenize(":z1 z2")).parse()))

    def test_parse_nested_hybrid_operators(self):
        self.assertTrue("((@z1 a) ∧ b) → (c | d)" == str(HybridSpatioTemporalParser(tokenize("(@z1 a & b) -> (c | d)")).parse()))
        self.assertTrue("(↓z((@z1 a) ∧ b)) → (↓z2(c | d))" == str(HybridSpatioTemporalParser(tokenize(":z(@z1 a & b) -> :z2(c | d)")).parse()))

    def test_parse_simple_spatial_operators(self):
        self.assertTrue("Left a" == str(HybridSpatioTemporalParser(tokenize("Left(a)")).parse()))
        self.assertTrue("Right b" == str(HybridSpatioTemporalParser(tokenize("Right b")).parse()))
        self.assertTrue("Front a" == str(HybridSpatioTemporalParser(tokenize("Front(a)")).parse()))
        self.assertTrue("Back b" == str(HybridSpatioTemporalParser(tokenize("Back b")).parse()))

    def test_parse_nested_spatial_operators(self):
        self.assertTrue("(Left a) ↔ (@z1(Back(a | b)))" == str(HybridSpatioTemporalParser(tokenize("(Left(a)) <-> (@z1 Back(a | b))")).parse()))

    def test_parse_syntactically_wrong_formulas(self):
        pass
if __name__ == '__main__':
    unittest.main()
