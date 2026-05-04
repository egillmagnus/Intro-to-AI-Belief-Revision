from __future__ import annotations

from .formula import Formula, Not, parse
from .belief_base import BeliefBase
from .contraction import contract


def expand(bb: BeliefBase, formula: Formula | str, priority: int = 1) -> BeliefBase:
    if isinstance(formula, str):
        formula = parse(formula)

    result = BeliefBase()
    for b in bb.beliefs:
        result.add(b.formula, b.priority)
    result.add(formula, priority)
    return result


def revise(bb: BeliefBase, formula: Formula | str, priority: int = 1) -> BeliefBase:
    # Levi identity: B * phi = (B / ~phi) + phi
    if isinstance(formula, str):
        formula = parse(formula)

    contracted = contract(bb, Not(formula))
    return expand(contracted, formula, priority)
