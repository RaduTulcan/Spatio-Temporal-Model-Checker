import re

from optimized_version.formula_types_optimized.HybridOperators import Nom, At, Bind
from optimized_version.parsers_optimized.SpatioTemporalFormulaParser import SPATIOTEMPORAL_TOKEN_REGEX, SpatioTemporalParser
from optimized_version.formula_types_optimized.ClassicalLogicOperator import Verum, Falsum, Prop, Not
from optimized_version.formula_types_optimized.SpatialOperators import Front, Back, Left, Right
from optimized_version.formula_types_optimized.TemporalOperators import Next, Eventually, Always

HYBRID_TOKEN_REGEX = r'''
    | (?P<NOM>z[0-9_]*)
    | (?P<AT>@z[0-9_]*)
    | (?P<BIND>↓z[0-9_]*)
'''

HYBRID_SPATIOTEMPORAL_TOKEN_REGEX = "".join([SPATIOTEMPORAL_TOKEN_REGEX, HYBRID_TOKEN_REGEX])

def tokenize(formula):
    tokens = []
    for match in re.finditer(HYBRID_SPATIOTEMPORAL_TOKEN_REGEX, formula, re.VERBOSE):
        kind = match.lastgroup
        value = match.group()
        if kind != "SPACE":
            tokens.append((kind, value))
    return tokens

class HybridSpatioTemporalParser(SpatioTemporalParser):
    def parse_unary(self):
        kind, value = self.peek()
        if kind in ("NOT", "FRONT", "BACK", "LEFT", "RIGHT", "NEXT", "EVENTUALLY", "ALWAYS", "AT", "BIND"):
            self.consume()
            operand = self.parse_unary()

            if kind == "NOT":
                return Not(value, operand)
            elif kind == "FRONT":
                return Front(value, operand)
            elif kind == "BACK":
                return Back(value, operand)
            elif kind == "LEFT":
                return Left(value, operand)
            elif kind == "RIGHT":
                return Right(value, operand)
            elif kind == "NEXT":
                return Next(value, operand)
            elif kind == "EVENTUALLY":
                return Eventually(value, operand)
            elif kind == "ALWAYS":
                return Always(value, operand)
            elif kind == "AT":
                return At(value[1:], value, operand)
            elif kind == "BIND":
                return Bind(value[1:], value, operand)
        elif kind == "LPAREN":
            self.consume("LPAREN")
            node = self.parse_iff()
            self.consume("RPAREN")
            return node
        elif kind == "PROP":
            return Prop(self.consume("PROP")[1])
        elif kind == "NOM":
            return Nom(self.consume("NOM")[1])
        elif kind == "TOP":
            self.consume("TOP")
            return Verum()
        elif kind == "BOT":
            self.consume("BOT")
            return Falsum()
        else:
            raise SyntaxError("Unexpected token:", kind)
