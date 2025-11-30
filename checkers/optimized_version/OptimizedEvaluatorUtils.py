import re
from typing import Optional, Union
from formula_types.HybridFormula import Nom
from formula_types.ClassicalLogicFormula import Verum, Not, Or
from formula_types.HybridSpatioTemporalFormula import HybridSpatioTemporalFormula
from formula_types.SpatialFormula import Front, Back, Left, Right

from parsers.HybridSpatioTemporalFormulaParser import HybridSpatioTemporalParser, tokenize

DIRECTIONS = {
    "Left": (0, 1),
    "Right": (0, -1),
    "Front": (1, 0),
    "Back": (-1, 0),
    "Stay": (0, 0),
}


def get_tokens(formula: str) -> list[str]:
    """
    Splits the input string in tokens.

    :param formula: the string of the logical formula
    :return: the list of tokens the formula is made of
    """
    spaced = formula.replace("(", " ( ").replace(")", " ) ")
    return [t for t in spaced.split() if t]


def strip_parentheses(tokens: list[str]) -> list[str]:
    """
    Removes the parentheses tokens from a list of tokens.

    :param tokens: the list of tokens
    :return: the list of tokens without parentheses
    """
    return [t for t in tokens if t not in ("(", ")")]


def parse_static_car(formula: str) -> Optional[str]:
    """
    Extracts static cars from the input formula.

    :param formula: logical formula
    :return: a list of static cars
    """
    parsed_formula: HybridSpatioTemporalFormula = HybridSpatioTemporalParser(tokenize(formula)).parse()
    tokens: list[str] = strip_parentheses(get_tokens(str(parsed_formula)))

    # formula has exactly 5 tokens (without parentheses)
    if len(tokens) != 5:
        return None

    # binder syntax must match
    if not re.fullmatch(r"↓z[0-9_]*", tokens[1]):
        return None

    # at syntax must match
    if not re.fullmatch(r"@z[0-9_]*", tokens[0]):
        return None

    # globally operator must exist
    if tokens[2] != "G":
        return None

    # binder nominal must match the last token
    if tokens[1][1:] != tokens[4]:
        return None

    # both @-occurrences must match
    if tokens[0] != tokens[3]:
        return None

    return tokens[0][1:]


def dirs_to_offset(dirs: list[str]) -> tuple[int, int]:
    """
    Converts a sequence of directions into a single offset.

    :param dirs: list of directions
    :return: a tuple representing the offset
    """
    x: int = 0
    y: int = 0
    for d in dirs:
        dx, dy = DIRECTIONS[d]
        x += dx
        y += dy
    return x, y


def dirs_to_offsets(dirs: list[str]) -> list[tuple[int, int]]:
    """
    Converts a sequence of directions in a sequence of offsets.

    :param dirs: the list of directions
    :return: the sequence of offsets
    """
    offsets: list[tuple[int, int]] = []
    for d in dirs:
        offsets.append(DIRECTIONS[d])
    return offsets


def parse_fixed_offset(formula: str) -> Union[tuple[str, str, tuple[int, int]], tuple[None, None, None]]:
    """
    Extracts dependent cars with their relative offset.

    :param formula: logical formula
    :return: the reference car, the dependent car and their offset
    """
    tokens: list[str] = strip_parentheses(get_tokens(formula))

    if tokens[0] != "G":
        return None, None, None

    if not re.fullmatch(r"@z[0-9_]*", tokens[1]):
        return None, None, None

    if not re.fullmatch(r"z[0-9_]*", tokens[-1]):
        return None, None, None

    directions: list[str] = tokens[2:-1]

    # check that all other tokens are only directions
    if len(directions) == 0:
        return None, None, None

    for d in directions:
        if d != "Left" and d != "Right" and d != "Back" and d != "Front":
            return None, None, None

    reference_car: str = tokens[1][1:]
    dependent_car: str = tokens[-1]
    offset: tuple[int, int] = dirs_to_offset(directions)
    return reference_car, dependent_car, offset


def branches_of(fml: HybridSpatioTemporalFormula) -> list[HybridSpatioTemporalFormula]:
    """
    Returns a list of disjuncts for a (nested) disjunction.

    :param fml: logical formula
    :return: list of disjuncts
    """
    if isinstance(fml, Or):
        return branches_of(fml.left) + branches_of(fml.right)
    else:
        return [fml]


def debranch(fml: HybridSpatioTemporalFormula) -> HybridSpatioTemporalFormula:
    """
    Returns the first branch of a (nested) disjunction.
    :param fml: logical formula
    :return: first disjunct
    """
    return branches_of(fml)[0]


#
def is_end_check(fml: HybridSpatioTemporalFormula) -> bool:
    """
    Returns whether fml is an end-checking formula (! X 1).

    :param fml: logical formula
    :return: true if it is an end-checking formula, false otherwise
    """
    if not isinstance(fml, Not):
        return False
    next: HybridSpatioTemporalFormula = fml.operand
    if next.op != "X":
        return False
    return isinstance(next.operand, Verum)


def strip_end_check(fml: HybridSpatioTemporalFormula) -> Optional[HybridSpatioTemporalFormula]:
    """
    Removes the end-check disjunct.

    :param fml: logical formula
    :return: the first disjunct in the list of disjuncts
    """
    if fml.op != "∨":
        return fml
    branches: list[HybridSpatioTemporalFormula] = branches_of(fml)
    clean_branches: list[HybridSpatioTemporalFormula] = [x for x in branches if not is_end_check(x)]
    if len(clean_branches) != 1:
        return None
    return clean_branches[0]


def get_movement_pattern(fml: HybridSpatioTemporalFormula) -> Optional[
    tuple[str, str, list[HybridSpatioTemporalFormula]]]:
    """
    Unpacks the syntactic pattern used in movement specs:  G @ ↓ X @

    :param fml: logical formula
    :return:
    """

    if fml.op != "G":
        return None
    at_outer: HybridSpatioTemporalFormula = fml.operand
    if not hasattr(at_outer, 'op'):
        return None
    if at_outer.op[0] != "@":
        return None
    arrow: HybridSpatioTemporalFormula = at_outer.operand
    if arrow.op[0] != "↓":
        return None
    next: HybridSpatioTemporalFormula = strip_end_check(arrow.operand)
    if next is None or next.op != "X":
        return None
    at_inner: HybridSpatioTemporalFormula = next.operand
    if at_inner.op[0] != "@":
        return None
    if at_outer.op != at_inner.op:
        return None
    vehicle: str = at_outer.name
    tmp_var: str = arrow.name
    inner_branches: list[HybridSpatioTemporalFormula] = branches_of(at_inner.operand)
    return vehicle, tmp_var, inner_branches


def is_left_of(fml, tmp_var): return isinstance(fml, Left) and fml.operand.name == tmp_var


def is_right_of(fml: HybridSpatioTemporalFormula, tmp_var: str) -> bool:
    """
    Checks whether the temporary variable is argument to Right operator.

    :param fml: logical formula
    :param tmp_var: temporary nominal variable
    :return: true if argument, false otherwise
    """
    return isinstance(fml, Right) and fml.operand.name == tmp_var


def is_front_of(fml: HybridSpatioTemporalFormula, tmp_var: str) -> bool:
    """
    Checks whether the temporary variable is argument to Front operator.

    :param fml: logical formula
    :param tmp_var: temporary nominal variable
    :return: true if argument, false otherwise
    """

    return isinstance(fml, Front) and fml.operand.name == tmp_var


def is_back_of(fml: HybridSpatioTemporalFormula, tmp_var: str) -> bool:
    """
    Checks whether the temporary variable is argument to Back operator.

    :param fml: logical formula
    :param tmp_var: temporary nominal variable
    :return: true if argument, false otherwise
    """
    return isinstance(fml, Back) and fml.operand.name == tmp_var


def is_stay_of(fml: HybridSpatioTemporalFormula, tmp_var: str) -> bool:
    """
    Checks whether the temporary variable is a nominal.

    :param fml: logical formula
    :param tmp_var: temporary nominal variable
    :return: true if argument, false otherwise
    """
    return isinstance(fml, Nom) and fml.name == tmp_var


def branches_to_directions(inner_branches: list[HybridSpatioTemporalFormula], tmp_var: str) -> Optional[list[str]]:
    """
    Creates a list of directions based on existing branches.

    :param inner_branches: a list of branches
    :param tmp_var: temporary variable
    :return: list of directions
    """
    lefts: list[HybridSpatioTemporalFormula] = [x for x in inner_branches if is_left_of(x, tmp_var)]
    rights: list[HybridSpatioTemporalFormula] = [x for x in inner_branches if is_right_of(x, tmp_var)]
    fronts: list[HybridSpatioTemporalFormula] = [x for x in inner_branches if is_front_of(x, tmp_var)]
    backs: list[HybridSpatioTemporalFormula] = [x for x in inner_branches if is_back_of(x, tmp_var)]
    stays: list[HybridSpatioTemporalFormula] = [x for x in inner_branches if is_stay_of(x, tmp_var)]
    stops: list[HybridSpatioTemporalFormula] = [x for x in inner_branches if is_end_check(x)]
    extras: list[HybridSpatioTemporalFormula] = [x for x in inner_branches if
                                                 not x in (lefts + rights + fronts + backs + stays + stops)]
    if len(extras) > 0:
        return None
    directions: list[str] = []
    if len(lefts) > 0: directions = directions + ["Left"]
    if len(rights) > 0: directions = directions + ["Right"]
    if len(fronts) > 0: directions = directions + ["Front"]
    if len(backs) > 0: directions = directions + ["Back"]
    if len(stays) > 0: directions = directions + ["Stay"]
    return directions


def parse_fixed_movement(formula: HybridSpatioTemporalFormula) -> Union[
    tuple[None, None], tuple[str, list[tuple[int, int]]]]:
    """
    Extracts fixed movement car from the input formula.

    :param formula: logic formula
    :return: car name and offset
    """
    pat: tuple[str, str, list[HybridSpatioTemporalFormula]] = get_movement_pattern(debranch(formula))
    if pat is None:
        return None, None
    car, tmp_var, inner_branches = pat
    directions: list[str] = branches_to_directions(inner_branches, tmp_var)
    if directions is None:
        return None, None

    offsets: list[tuple[int, int]] = dirs_to_offsets(directions)
    return car, offsets
