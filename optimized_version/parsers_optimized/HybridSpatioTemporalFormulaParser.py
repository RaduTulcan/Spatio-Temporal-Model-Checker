import re

from HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from optimized_version.formula_types_optimized.HybridFormula import Nom, At, Bind
from optimized_version.parsers_optimized.SpatioTemporalFormulaParser import SPATIOTEMPORAL_TOKEN_REGEX, SpatioTemporalParser
from optimized_version.formula_types_optimized.ClassicalLogicFormula import Verum, Falsum, Prop, Not
from optimized_version.formula_types_optimized.SpatialFormula import Front, Back, Left, Right
from optimized_version.formula_types_optimized.TemporalFormula import Next, Eventually, Always


NOM = "NOM"
AT = "AT"
BIND = "BIND"
NEXT = "NEXT"
EVENTUALLY = "EVENTUALLY"
ALWAYS = "ALWAYS"
UNTIL = "UNTIL"
SPACE = "SPACE"
AND = "AND"
TOP = "TOP"
BOT = "BOT"
NOT = "NOT"
FRONT = "FRONT"
BACK = "BACK"
LEFT = "LEFT"
RIGHT = "RIGHT"
LPAREN = "LPAREN"
RPAREN = "RPAREN"
PROP = "PROP"

# regex for hybrid syntax
HYBRID_TOKEN_REGEX: str = r'''
    | (?P<''' + NOM + '''>z[0-9_]*)
    | (?P<''' + AT + '''>@z[0-9_]*)
    | (?P<''' + BIND + '''>[↓:]z[0-9_]*)
'''

# regex for hybrid spatio-temporal formulas
HYBRID_SPATIOTEMPORAL_TOKEN_REGEX: str = "".join([SPATIOTEMPORAL_TOKEN_REGEX, HYBRID_TOKEN_REGEX])


def tokenize(formula: str) -> list[tuple[str, str]]:
    """
    Splits the input formula strings into tokens.
    :param formula: the hybrid spatio-temporal formula
    :return: a list of tokens/syntactic constructs the formula string is made up of
    """
    tokens: list[tuple[str, str]] = []
    for match in re.finditer(HYBRID_SPATIOTEMPORAL_TOKEN_REGEX, formula, re.VERBOSE):
        kind: str = match.lastgroup
        value: str = match.group()
        if kind != SPACE:
            tokens.append((kind, value))
    return tokens


class HybridSpatioTemporalParser(SpatioTemporalParser):
    def parse_unary(self) -> HybridSpatioTemporalFormula:
        """
        Parses unary hybrid spatio-temporal formulas.
        :return: returns the parsed formula
        """
        kind: str
        value: str
        kind, value = self.peek()
        if kind in (NOT, FRONT, BACK, LEFT, RIGHT, NEXT, EVENTUALLY, ALWAYS, AT, BIND):
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
            elif kind == AT:
                return At(value[1:], value, operand)
            elif kind == BIND:
                return Bind(value[1:], value.replace(":","↓"), operand)
        elif kind == LPAREN:
            self.consume(LPAREN)
            node: HybridSpatioTemporalFormula = self.parse_iff()
            self.consume(RPAREN)
            return node
        elif kind == PROP:
            return Prop(self.consume(PROP)[1])
        elif kind == NOM:
            return Nom(self.consume(NOM)[1])
        elif kind == TOP:
            self.consume(TOP)
            return Verum()
        elif kind == BOT:
            self.consume(BOT)
            return Falsum()
        else:
            raise SyntaxError(f"Unexpected token {self.peek()}")
