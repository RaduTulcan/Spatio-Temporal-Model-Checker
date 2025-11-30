import re
from typing import Union
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from formula_types.HybridFormula import Nom, At, Bind
from formula_types.ClassicalLogicFormula import Verum, Falsum, Prop, Not, And, Iff, If, Or
from formula_types.SpatialFormula import Front, Back, Left, Right
from formula_types.TemporalFormula import Next, Eventually, Always, Until

# classical logic syntax components
TOP = "TOP"
BOT = "BOT"
PROP = "PROP"
NOT = "NOT"
AND = "AND"
OR = "OR"
IMPLIES = "IMPLIES"
IFF = "IFF"

# hybrid logic syntax components
NOM = "NOM"
AT = "AT"
BIND = "BIND"

# temporal logic syntax components
NEXT = "NEXT"
EVENTUALLY = "EVENTUALLY"
ALWAYS = "ALWAYS"
UNTIL = "UNTIL"

# spatial logic components
FRONT = "FRONT"
BACK = "BACK"
LEFT = "LEFT"
RIGHT = "RIGHT"

# other syntax components
SPACE = "SPACE"
LPAREN = "LPAREN"
RPAREN = "RPAREN"

# regex for hybrid spatio-temporal formulas
HYBRID_SPATIOTEMPORAL_TOKEN_REGEX: str = r'''
    (?P<''' + TOP + '''>⊤|1)
  | (?P<''' + BOT + '''>⊥|0)
  | (?P<''' + NOT + '''>¬|!)
  | (?P<''' + AND + '''>∧|&)
  | (?P<''' + OR + '''>v|\|)
  | (?P<''' + IMPLIES + '''>→|->)
  | (?P<''' + IFF + '''>↔|<->)
  | (?P<''' + FRONT + '''>Front) 
  | (?P<''' + BACK + '''>Back)
  | (?P<''' + LEFT + '''>Left)
  | (?P<''' + RIGHT + '''>Right)
  | (?P<''' + LPAREN + '''>\()
  | (?P<''' + RPAREN + '''>\))
  | (?P<''' + PROP + '''>[a-y][a-y0-9_]*)
  | (?P<''' + SPACE + '''>\s+)
  | (?P<''' + NOM + '''>z[0-9_]*)
  | (?P<''' + AT + '''>@z[0-9_]*)
  | (?P<''' + BIND + '''>[↓:]z[0-9_]*)
  | (?P<''' + NEXT + '''>X)
  | (?P<''' + EVENTUALLY + '''>F)
  | (?P<''' + ALWAYS + '''>G)
  | (?P<''' + UNTIL + '''>U)
  '''


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


class HybridSpatioTemporalParser:
    """
    Class for the hybrid spatio-temporal formula parser
    """

    def __init__(self, tokens: list[tuple[str, str]]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Union[tuple[str, str], tuple[None, None]]:
        """
        Returns the next token in the array of tokens.

        :return: the next token
        """
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def consume(self, expected: str = None) -> tuple[str, str]:
        """
        Consumes the tokens one-by one and matches it against the expected string.

        :param expected: string for the expected symbol
        :return: the parsed token
        """
        tok = self.peek()
        if expected and tok[0] != expected:
            raise SyntaxError(f"Expected {expected}, got {tok}")
        self.pos += 1
        return tok

    def parse(self) -> HybridSpatioTemporalFormula:
        """
        Parses a hybrid spatio-temporal formula.

        :return: the parsed hybrid spatio-temporal formula
        """
        node: HybridSpatioTemporalFormula = self.parse_iff()
        if self.pos != len(self.tokens):
            raise SyntaxError("Unexpected tokens at end")
        return node

    def parse_iff(self) -> HybridSpatioTemporalFormula:
        """
        Parses a hybrid spatio-temporal formula with the uppermost operator a bi-implication.

        :return: the parsed hybrid spatio-temporal formula
        """
        node: HybridSpatioTemporalFormula = self.parse_implies()
        while self.peek()[0] == IFF:
            self.consume()
            right: HybridSpatioTemporalFormula = self.parse_implies()
            node = Iff("↔", node, right)
        return node

    def parse_implies(self) -> HybridSpatioTemporalFormula:
        """
        Parses a hybrid spatio-temporal formula with the uppermost operator an implication.

        :return: the parsed hybrid spatio-temporal formula
        """
        node: HybridSpatioTemporalFormula = self.parse_or()
        while self.peek()[0] == IMPLIES:
            self.consume()
            right: HybridSpatioTemporalFormula = self.parse_or()
            node = If("→", node, right)
        return node

    def parse_or(self) -> HybridSpatioTemporalFormula:
        """
        Parses a hybrid spatio-temporal formula with the uppermost operator a disjunction.

        :return: the parsed hybrid spatio-temporal formula
        """
        node: HybridSpatioTemporalFormula = self.parse_and()
        while self.peek()[0] == OR:
            self.consume()
            right: HybridSpatioTemporalFormula = self.parse_and()
            node = Or("∨", node, right)
        return node

    def parse_and(self) -> HybridSpatioTemporalFormula:
        """
        Parses a hybrid spatio-temporal formula with the uppermost operator a conjunction.

        :return: the parsed hybrid spatio-temporal formula
        """
        node: HybridSpatioTemporalFormula = self.parse_until()
        while self.peek()[0] == AND:
            self.consume()
            right: HybridSpatioTemporalFormula = self.parse_until()
            node = And("∧", node, right)
        return node

    def parse_until(self) -> HybridSpatioTemporalFormula:
        """
        Parses a hybrid spatio-temporal formula with the uppermost operator temporal until.

        :return: the parsed hybrid spatio-temporal formula
        """
        node: HybridSpatioTemporalFormula = self.parse_unary()
        while self.peek()[0] == UNTIL:
            self.consume()
            right: HybridSpatioTemporalFormula = self.parse_unary()
            node = Until("U", node, right)
        return node

    def parse_unary(self) -> HybridSpatioTemporalFormula:
        """
        Parses a hybrid spatio-temporal formula with the uppermost operator a unary operator.

        :return: the parsed hybrid spatio-temporal formula
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
                return Bind(value[1:], value.replace(":", "↓"), operand)
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
