import re

from HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from optimized_version.parsers_optimized.SpatialFormulaParser import SPATIAL_TOKEN_REGEX, SpatialParser
from optimized_version.formula_types_optimized.ClassicalLogicFormula import Verum, Falsum, Prop, Not, And
from optimized_version.formula_types_optimized.SpatialFormula import Front, Back, Left, Right
from optimized_version.formula_types_optimized.TemporalFormula import Next, Eventually, Always, Until

NEXT = "NEXT"
EVENTUALLY = "EVENTUALLY"
ALWAYS = "ALWAYS"
UNTIL = "UNTIL"
SPACE = "SPACE"
AND = "AND"
TOP = "TOP"
BOT = "BOT"
NOT = "NOT"
AND = "AND"
OR = "OR"
IMPLIES = "IMPLIES"
IFF = "IFF"
FRONT = "FRONT"
BACK = "BACK"
LEFT = "LEFT"
RIGHT = "RIGHT"
LPAREN = "LPAREN"
RPAREN = "RPAREN"
PROP = "PROP"
SPACE = "SPACE"

# regex for temporal syntax
TEMPORAL_TOKEN_REGEX = r'''
  | (?P<''' + NEXT + '''>X)
  | (?P<''' + EVENTUALLY + '''>F)
  | (?P<''' + ALWAYS + '''>G)
  | (?P<''' + UNTIL + '''>U)'''

# regex for spatio-temporal formulas
SPATIOTEMPORAL_TOKEN_REGEX = "".join([SPATIAL_TOKEN_REGEX, TEMPORAL_TOKEN_REGEX])


def tokenize(formula: str) -> list[tuple[str, str]]:
    """
    Splits the input formula strings into tokens.
    :param formula: the hybrid spatio-temporal formula
    :return: a list of tokens/syntactic constructs the formula string is made up of
    """
    tokens: list[tuple[str, str]] = []
    for match in re.finditer(SPATIOTEMPORAL_TOKEN_REGEX, formula, re.VERBOSE):
        kind: str = match.lastgroup
        value: str = match.group()
        if kind != SPACE:
            tokens.append((kind, value))
    return tokens


class SpatioTemporalParser(SpatialParser):

    def parse_and(self) -> HybridSpatioTemporalFormula:
        """
        Parses formulas that are conjunctions.
        :return: the parsed conjunction
        """
        node: HybridSpatioTemporalFormula = self.parse_until()
        while self.peek()[0] == AND:
            self.consume()
            right: HybridSpatioTemporalFormula = self.parse_until()
            node = And("∧", node, right)
        return node

    def parse_until(self) -> HybridSpatioTemporalFormula:
        """
        Parses temporal until formulas.
        :return: the parsed formula
        """
        node: HybridSpatioTemporalFormula = self.parse_unary()
        while self.peek()[0] == UNTIL:
            self.consume()
            right: HybridSpatioTemporalFormula = self.parse_unary()
            node = Until("U", node, right)
        return node

    def parse_unary(self) -> HybridSpatioTemporalFormula:
        """
        Parses unary hybrid spatio-temporal formulas.
        :return: returns the parsed formula
        """
        kind: str
        value: str
        kind, value = self.peek()

        if kind in (NOT, FRONT, BACK, LEFT, RIGHT, NEXT, EVENTUALLY, ALWAYS):
            self.consume()
            operand: HybridSpatioTemporalFormula = self.parse_unary()

            if kind == NOT:
                return Not(value, operand)
            elif kind == FRONT:
                return Front(value, operand)
            elif kind == BACK:
                return Back(value, operand)
            elif kind == LEFT:
                return Left(value, operand)
            elif kind == RIGHT:
                return Right(value, operand)
            elif kind == NEXT:
                return Next(value, operand)
            elif kind == EVENTUALLY:
                return Eventually(value, operand)
            elif kind == ALWAYS:
                return Always(value, operand)
        elif kind == LPAREN:
            self.consume(LPAREN)
            node: HybridSpatioTemporalFormula = self.parse_iff()
            self.consume(RPAREN)
            return node
        elif kind == PROP:
            return Prop(self.consume(PROP)[1])
        elif kind == TOP:
            self.consume(TOP)
            return Verum()
        elif kind == BOT:
            self.consume(BOT)
            return Falsum()
        else:
            raise SyntaxError(f"Unexpected token {self.peek()}")
