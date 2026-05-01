"""
Partial Meet Contraction for Belief Bases.

Given a belief base B and a formula φ, the contraction B ÷ φ removes enough
beliefs from B so that φ is no longer entailed, while retaining as much of B
as possible.

Algorithm (from the course slides / AGM theory):

1. Compute B⊥φ — the set of all MAXIMAL subsets of B that do NOT entail φ.
   (These are called "remainder sets".)

2. Apply a selection function γ to choose a non-empty sub-collection of B⊥φ.
   We use a priority-based selection function:
   γ(B⊥φ) = those remainder sets that have the maximum total priority sum,
   i.e., we prefer to keep the most entrenched beliefs.

3. Return the intersection ∩ γ(B⊥φ).

If B does not entail φ (vacuous case) the original base is returned unchanged.
If B⊥φ is empty (φ is a tautology or B is empty), we return an empty base.
"""

from __future__ import annotations
from typing import List, FrozenSet
from itertools import combinations

from .formula import Formula, parse
from .belief_base import BeliefBase, Belief
from .entailment import entails


# ---------------------------------------------------------------------------
# Compute all maximal non-entailing subsets (B⊥φ)
# ---------------------------------------------------------------------------

def _compute_remainder_sets(beliefs: List[Belief], formula: Formula) -> List[FrozenSet[Belief]]:
    """
    Return B⊥formula: all maximal subsets of beliefs that do NOT entail formula.

    Approach: enumerate all subsets from largest to smallest.
    Keep a subset if:
      (a) it does not entail formula, AND
      (b) it is not already a subset of a known remainder set (maximality).
    """
    n = len(beliefs)
    remainder_sets: List[FrozenSet[Belief]] = []

    # Try subsets from largest to smallest so we find maximal ones first
    for size in range(n, 0, -1):
        for subset_tuple in combinations(beliefs, size):
            subset = frozenset(subset_tuple)
            subset_formulas = [b.formula for b in subset]

            # Skip if this subset entails formula
            if entails(subset_formulas, formula):
                continue

            # Skip if already dominated by a known remainder set
            # (i.e., this subset is a strict subset of something already found)
            dominated = any(subset < existing for existing in remainder_sets)
            if dominated:
                continue

            remainder_sets.append(subset)

    return remainder_sets


# ---------------------------------------------------------------------------
# Selection function
# ---------------------------------------------------------------------------

def _priority_score(remainder: FrozenSet[Belief]) -> int:
    """Score a remainder set by the sum of its beliefs' priorities."""
    return sum(b.priority for b in remainder)


def _select(remainders: List[FrozenSet[Belief]]) -> List[FrozenSet[Belief]]:
    """
    Priority-based selection function γ:
    Select the remainder set(s) with the highest total priority score.
    """
    if not remainders:
        return []
    max_score = max(_priority_score(r) for r in remainders)
    return [r for r in remainders if _priority_score(r) == max_score]


# ---------------------------------------------------------------------------
# Public contraction API
# ---------------------------------------------------------------------------

def contract(bb: BeliefBase, formula: Formula | str) -> BeliefBase:
    """
    Compute and return a NEW belief base: B ÷ formula.

    Uses partial meet contraction with priority-based selection.
    The original belief base is NOT modified.
    """
    if isinstance(formula, str):
        formula = parse(formula)

    beliefs = bb.beliefs  # sorted by priority descending

    # Vacuous case: if B does not entail φ, return B unchanged
    if not entails(bb.formulas, formula):
        result = BeliefBase()
        for b in beliefs:
            result.add(b.formula, b.priority)
        return result

    # Compute all maximal non-entailing subsets
    remainders = _compute_remainder_sets(beliefs, formula)

    # φ is a tautology or base is empty — return empty base
    if not remainders:
        return BeliefBase()

    # Apply selection function: pick highest-priority remainder sets
    selected = _select(remainders)

    # Take intersection of selected remainder sets
    intersection = selected[0]
    for r in selected[1:]:
        intersection = intersection & r

    # Build new belief base from the intersection
    result = BeliefBase()
    for b in intersection:
        result.add(b.formula, b.priority)

    return result
