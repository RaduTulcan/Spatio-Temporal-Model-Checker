import re
from SpatialFormulaParser import SPATIAL_TOKEN_REGEX, SpatialParser
from SpatioTemporalFormula import And, Not, Left, Right, Front, Back, Verum, Falsum, Prop

TEMPORAL_TOKEN_REGEX = r'''
  | (?P<NEXT>X)
  | (?P<EVENTUALLY>F)
  | (?P<ALWAYS>G)
  | (?P<UNTIL>U)'''

SPATIOTEMPORAL_TOKEN_REGEX = "".join([SPATIAL_TOKEN_REGEX, TEMPORAL_TOKEN_REGEX])


def tokenize(formula):
    tokens = []
    for match in re.finditer(SPATIOTEMPORAL_TOKEN_REGEX, formula, re.VERBOSE):
        kind = match.lastgroup
        value = match.group()
        if kind != "SPACE":
            tokens.append((kind, value))
    return tokens


class SpatioTemporalParser(SpatialParser):

    def parse_and(self):
        node = self.parse_until()
        while self.peek()[0] == "AND":
            self.consume()
            right = self.parse_until()
            node = And("∧", node, right)
        return node

    def parse_until(self):
        node = self.parse_unary()
        while self.peek()[0] == "U":
            self.consume("U")
            right = self.parse_unary()
            node = Until("U", node, right)
        return node

    def parse_unary(self):
        kind, value = self.peek()
        if kind in ("NOT", "FRONT", "BACK", "LEFT", "RIGHT", "NEXT", "EVENTUALLY", "ALWAYS"):
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
        elif kind == "LPAREN":
            self.consume("LPAREN")
            node = self.parse_iff()
            self.consume("RPAREN")
            return node
        elif kind == "PROP":
            return Prop(self.consume("PROP")[1])
        elif kind == "TOP":
            self.consume("TOP")
            return Verum()
        elif kind == "BOT":
            self.consume("BOT")
            return Falsum()
        else:
            raise SyntaxError(f"Unexpected token {self.peek()}")

    def parse_binary(self):
