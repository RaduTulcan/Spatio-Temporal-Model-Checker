import re
from baseline_version.formula_types_baseline.ClassicalLogicFormula import Iff, If, Or, And, Not, Prop, Verum, Falsum
from baseline_version.formula_types_baseline.SpatialFormula import Front, Back, Left, Right

SPATIAL_TOKEN_REGEX = r'''
    (?P<TOP>⊤)
  | (?P<BOT>⊥)
  | (?P<NOT>¬|~|!)
  | (?P<AND>∧|&)
  | (?P<OR>v|\|)
  | (?P<IMPLIES>→|->)
  | (?P<IFF>↔|<->)
  | (?P<FRONT>Front) 
  | (?P<BACK>Back)
  | (?P<LEFT>Left)
  | (?P<RIGHT>Right)
  | (?P<LPAREN>\()
  | (?P<RPAREN>\))
  | (?P<PROP>[a-y][a-y0-9_]*)
  | (?P<SPACE>\s+)'''

def tokenize(formula: str) -> list[tuple[str, str]]:
    """
    Splits the input formula strings into tokens.
    :param formula: the hybrid spatio-temporal formula
    :return: a list of tokens/syntactic constructs the formula string is made up of
    """
    tokens: list[tuple[str, str]] = []
    for match in re.finditer(SPATIAL_TOKEN_REGEX, formula, re.VERBOSE):
        kind: str = match.lastgroup
        value: str = match.group()
        if kind != "SPACE":
            tokens.append((kind, value))
    return tokens

class SpatialParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def consume(self, expected=None):
        tok = self.peek()
        if expected and tok[0] != expected:
            raise SyntaxError(f"Expected {expected}, got {tok}")
        self.pos += 1
        return tok

    def parse(self):
        node = self.parse_iff()
        if self.pos != len(self.tokens):
            raise SyntaxError("Unexpected tokens at end")
        return node

    def parse_iff(self):
        node = self.parse_implies()
        while self.peek()[0] == "IFF":
            self.consume()
            right = self.parse_implies()
            node = Iff("↔", node, right)
        return node

    def parse_implies(self):
        node = self.parse_or()
        while self.peek()[0] == "IMPLIES":
            self.consume()
            right = self.parse_or()
            node = If("→", node, right)
        return node

    def parse_or(self):
        node = self.parse_and()
        while self.peek()[0] == "OR":
            self.consume()
            right = self.parse_and()
            node = Or("∨", node, right)
        return node

    def parse_and(self):
        node = self.parse_unary()
        while self.peek()[0] == "AND":
            self.consume()
            right = self.parse_unary()
            node = And("∧", node, right)
        return node

    def parse_unary(self):
        kind, value = self.peek()
        if kind in ("NOT", "FRONT", "BACK", "LEFT", "RIGHT"):
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
