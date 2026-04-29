"""
Expansion and Revision of a Belief Base.

Expansion:  B + φ  =  B ∪ {φ}
  Simply add the new formula to the belief base.

Revision:   B * φ  =  (B ÷ ¬φ) + φ       [Levi Identity]
  1. Contract by ¬φ  (remove enough beliefs so ¬φ is no longer entailed)
  2. Expand with φ   (add the new information)

The Levi identity is the standard AGM construction linking
contraction and revision.
"""

from __future__ import annotations

from .formula import Formula, Not, parse
from .belief_base import BeliefBase
from .contraction import contract


# ---------------------------------------------------------------------------
# Expansion
# ---------------------------------------------------------------------------

def expand(bb: BeliefBase, formula: Formula | str, priority: int = 1) -> BeliefBase:
    """
    Return a NEW belief base B + formula.

    The new formula is added with the given priority.
    The original belief base is NOT modified.
    """
    if isinstance(formula, str):
        formula = parse(formula)

    result = BeliefBase()
    for b in bb.beliefs:
        result.add(b.formula, b.priority)
    result.add(formula, priority)
    return result


# ---------------------------------------------------------------------------
# Revision  (Levi Identity)
# ---------------------------------------------------------------------------

def revise(bb: BeliefBase, formula: Formula | str, priority: int = 1) -> BeliefBase:
    """
    Return a NEW belief base B * formula, computed via the Levi Identity:
        B * φ = (B ÷ ¬φ) + φ

    Parameters
    ----------
    bb       : the current belief base
    formula  : the new formula to revise by (can be string or Formula)
    priority : entrenchment priority assigned to the new formula (default=1)
    """
    if isinstance(formula, str):
        formula = parse(formula)

    # Step 1: contract by ¬φ
    neg_formula = Not(formula)
    contracted = contract(bb, neg_formula)

    # Step 2: expand with φ
    revised = expand(contracted, formula, priority)
    return revised
