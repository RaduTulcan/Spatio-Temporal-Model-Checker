from BinaryFormula import BinaryFormula
from HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from UnaryFormula import UnaryFormula


class Verum(HybridSpatioTemporalFormula):
    """
    Class for logical constant "true".
    """
    def __repr__(self) -> str:
        return "⊤"

    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return True


class Falsum(HybridSpatioTemporalFormula):
    """
    Class for logical constant "false".
    """
    def __repr__(self) -> str:
        return "⊥"

    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return False


class Prop(HybridSpatioTemporalFormula):
    """
       Class for logical propositions.
    """
    def __init__(self, name: str):
        self.name: str = name

    def __repr__(self) -> str:
        return self.name

    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return self.name in grid[0][point[0]][point[1]]


# --------------------------------------------------------------------------
# 1-ary operators
# --------------------------------------------------------------------------
class Not(UnaryFormula):
    """
       Class for logical negation.
    """
    def evaluate(self, grid: list[list[list[list]]], point: tuple[int,int]) -> bool:
        return not self.operand.evaluate(grid, point)


# --------------------------------------------------------------------------
# 2-ary operators
# --------------------------------------------------------------------------


class And(BinaryFormula):
    """
       Class for logical constant conjunction.
    """
    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return self.left.evaluate(grid, point) and self.right.evaluate(grid, point)

    def __repr__(self) -> str:
        return f"({self.left} {self.op} {self.right})"


class If(BinaryFormula):
    """
       Class for logical implication.
    """
    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return (not self.left.evaluate(grid, point)) or self.right.evaluate(grid, point)

    def __repr__(self) -> str:
        return f"({self.left} {self.op} {self.right})"


class Iff(BinaryFormula):
    """
       Class for logical bi-implication.
    """
    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return ((not self.left.evaluate(grid, point)) or self.right.evaluate(grid, point)) and (
                (not self.right.evaluate(grid, point)) or self.left.evaluate(grid, point))

    def __repr__(self) -> str:
        return f"({self.left} {self.op} {self.right})"


class Or(BinaryFormula):
    """
       Class for logical disjunction.
    """
    def evaluate(self, grid: list[list[list[list]]], point: tuple[int, int]) -> bool:
        return self.left.evaluate(grid, point) or self.right.evaluate(grid, point)

    def __repr__(self) -> str:
        return f"({self.left} {self.op} {self.right})"
