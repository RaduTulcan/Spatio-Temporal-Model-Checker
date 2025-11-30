import re
from formula_types.HybridFormula import Nom, At, Bind
from formula_types.ClassicalLogicFormula import Verum, Falsum, Prop, Not, And, Or
from formula_types.SpatialFormula import Front, Back, Left, Right
from itertools import chain, combinations, product

DIRECTIONS = {
    "Left": (0, 1),
    "Right": (0, -1),
    "Front": (1, 0),
    "Back": (-1, 0),
    "Stay": (0, 0),
}

def get_tokens(formula: str):
    spaced = formula.replace("(", " ( ").replace(")", " ) ")
    return [t for t in spaced.split() if t]

def strip_parentheses(tokens):
    return [t for t in tokens if t not in ("(", ")")]

def parse_static_car(formula: str):
    tokens = strip_parentheses(get_tokens(formula))

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

def dirs_to_offset(dirs):
    x = y = 0
    for d in dirs:
        dx, dy = DIRECTIONS[d]
        x += dx
        y += dy
    return x, y

# apologies for similar name. Above function is used in a different branch of the code
# which I wish not to disturb
def dirs_to_offsets(dirs):
    offsets = []
    for d in dirs:
        offsets.append(DIRECTIONS[d])
    return offsets


def parse_fixed_offset(formula: str):
    tokens = strip_parentheses(get_tokens(formula))

    if tokens[0] != "G":
        return None, None, None

    if not re.fullmatch(r"@z[0-9_]*", tokens[1]):
        return None, None, None

    if not re.fullmatch(r"z[0-9_]*", tokens[-1]):
        return None, None, None

    directions = tokens[2:-1]

    # check that all other tokens are only directions
    if len(directions) == 0:
        return None, None, None

    for d in directions:
        if d != "Left" and d != "Right" and d != "Back" and d != "Front":
            return None, None, None

    reference_car = tokens[1][1:]
    dependent_car = tokens[-1]
    offset = dirs_to_offset(directions)
    return reference_car, dependent_car, offset


# If fml is a (nested) disjunction, return the list of disjuncts
def branches_of(fml):
    if isinstance(fml, Or):
        return branches_of(fml.left) + branches_of(fml.right)
    else:
        return [fml]


# If fml is a (nested) disjunction, return the first disjunct.
def debranch(fml):
    return branches_of(fml)[0]


# Returns whether fml is an end-checking formula (! X 1)
def is_end_check(fml):
    if not isinstance(fml, Not):
        return False
    next = fml.operand
    if next.op != "X":
        return False
    return isinstance(next.operand, Verum)


# remove disjunct (! X 1)
def strip_end_check(fml):
    if fml.op != "∨":
        return fml
    branches = branches_of(fml)
    clean_branches = [x for x in branches if not is_end_check(x)]
    if len(clean_branches) != 1:
        return None
    return clean_branches[0]


# Unpack the syntactic pattern used in movement specs:  G @ ↓ X @
def get_movement_pattern(fml):
    if fml.op != "G":
        return None
    at_outer = fml.operand
    if at_outer.op[0] != "@":
        return None
    arrow = at_outer.operand
    if arrow.op[0] != "↓":
        return None
    next = strip_end_check(arrow.operand)
    if next == None or next.op != "X":
        return None
    at_inner = next.operand
    if at_inner.op[0] != "@":
        return None
    if at_outer.op != at_inner.op:
        return None
    vehicle = at_outer.name
    tmp_var = arrow.name
    inner_branches = branches_of(at_inner.operand)
    return (vehicle, tmp_var, inner_branches)


def is_left_of(fml, tmp_var): return isinstance(fml, Left) and fml.operand.name == tmp_var


def is_right_of(fml, tmp_var): return isinstance(fml, Right) and fml.operand.name == tmp_var


def is_front_of(fml, tmp_var): return isinstance(fml, Front) and fml.operand.name == tmp_var


def is_back_of(fml, tmp_var): return isinstance(fml, Back) and fml.operand.name == tmp_var


def is_stay_of(fml, tmp_var): return isinstance(fml, Nom) and fml.name == tmp_var


def branches_to_directions(inner_branches, tmp_var):
    lefts = [x for x in inner_branches if is_left_of(x, tmp_var)]
    rights = [x for x in inner_branches if is_right_of(x, tmp_var)]
    fronts = [x for x in inner_branches if is_front_of(x, tmp_var)]
    backs = [x for x in inner_branches if is_back_of(x, tmp_var)]
    stays = [x for x in inner_branches if is_stay_of(x, tmp_var)]
    stops = [x for x in inner_branches if is_end_check(x)]
    extras = [x for x in inner_branches if not x in (lefts + rights + fronts + backs + stays + stops)]
    if len(extras) > 0:
        return None
    directions = []
    if (len(lefts) > 0): directions = directions + ["Left"]
    if (len(rights) > 0): directions = directions + ["Right"]
    if (len(fronts) > 0): directions = directions + ["Front"]
    if (len(backs) > 0): directions = directions + ["Back"]
    if (len(stays) > 0): directions = directions + ["Stay"]
    return directions


def parse_fixed_movement(fml_str, formula):
    # branches = [b.strip() for b in formula.split("|")]
    # first_branch = branches[0]
    # tokens_first = get_tokens(first_branch)

    # formula must start with globally operator
    # if tokens_first[0] != "G":
    #    return None, None

    # followed by at-operator and a nominal
    # if not re.fullmatch(r"@z[0-9_]*", tokens_first[1]):
    #    return None, None

    # followed by a binding operator
    # if not re.fullmatch(r"↓z[0-9_]*", tokens_first[2]):
    #    return None, None

    # followed by next operator
    # if tokens_first[3] != "X":
    #    return None, None

    # the nominals for at-operator must match
    # if tokens_first[1] != tokens_first[4]:
    #    return None, None

    # "free" nominals used after the binding operator must match the nominial of the operator
    # if tokens_first[-1] != tokens_first[2][1:]:
    #   return None, None
    pat = get_movement_pattern(debranch(formula))
    if pat == None:
        return None, None
    (car, tmp_var, inner_branches) = pat
    directions = branches_to_directions(inner_branches, tmp_var)
    if directions == None:
        return None, None
    # car   = tokens_first[1][1:]
    # directions = tokens_first[5:-1]

    # check that all other tokens are only directions
    # if len(directions) == 0:
    #    return None, None

    # for d in directions:
    # if d != "Left" and d != "Right" and d != "Back" and d != "Front":
    # return None, None

    offsets = dirs_to_offsets(directions)
    return car, offsets

    # for b in branches[1:]:
    # tok = get_tokens(b)
    # directions = tok[:-1]

    # "free" nominals used after the binding operator must match the nominial of the operator
    # if tok[-1] != tokens_first[2][1:]:
    # return None, None

#        for d in directions:
# if d != "Left" and d != "Right" and d != "Back" and d != "Front":
# return None, None

#        offsets.append(dirs_to_offset(directions))
