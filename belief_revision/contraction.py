"""
Partial Meet Contraction for Belief Bases.

Given a belief base B and a formula φ, the contraction B ÷ φ removes enough
beliefs from B so that φ is no longer entailed, while retaining as much of B
as possible.

Algorithm (from the course slides / AGM theory):

  1. Compute B⊥φ  — the set of all MAXIMAL subsets of B that do NOT entail φ.
     (These are called "remainder sets".)

  2. Apply a selection function γ to choose a non-empty sub-collection of B⊥φ.
     We use a priority-based selection function:
       γ(B⊥φ) = those remainder sets that have the maximum total priority sum,
     i.e., we prefer to keep the most entrenched beliefs.

  3. Return the intersection ∩ γ(B⊥φ).

If B does not entail φ (vacuous case) the original base is returned unchanged.
If B⊥φ is empty (φ is a tautology or B is empty), we return B unchanged
(we cannot remove a tautology).
"""

from __future__ import annotations
from typing import List, FrozenSet, Iterable

from .formula import Formula, parse
from .belief_base import BeliefBase, Belief
from .entailment import entails


# ---------------------------------------------------------------------------
# Helper: compute all maximal non-entailing subsets  (B⊥φ)
# ---------------------------------------------------------------------------

def _remainder_sets(beliefs: List[Belief], formula: Formula) -> List[FrozenSet[Belief]]:
    """
    Return B⊥formula: all maximal subsets of `beliefs` that do not entail `formula`.

    Uses a generate-and-test approach:
      - Start from the full set, iteratively try removing each belief.
      - A subset S is in B⊥φ iff:
          (a) S does not entail φ, AND
          (b) Adding any removed belief back would make it entail φ.

    We use a recursive power-set search pruned by maximality.
    """
    formulas_only = [b.formula for b in beliefs]

    # Quick check: if the full base does not entail φ, return {full set}
    if not entails(formulas_only, formula):
        return [frozenset(beliefs)]

    remainders: List[FrozenSet[Belief]] = []
    _find_remainders(beliefs, formula, frozenset(), 0, remainders)
    return remainders


def _find_remainders(
    beliefs: List[Belief],
    formula: Formula,
    current: FrozenSet[Belief],
    start_idx: int,
    results: List[FrozenSet[Belief]],
) -> None:
    """
    Recursive backtracking to find all maximal non-entailing subsets.

    We build subsets by deciding for each belief whether to include it.
    We only record a subset when:
      - It does not entail formula
      - No superset (within beliefs) also has this property (maximality).

    Approach: start from the empty set and grow it by adding one belief at a time.
    We prune: if adding a belief causes entailment of formula, skip that belief.
    """
    # Try adding beliefs from start_idx onward
    for i in range(start_idx, len(beliefs)):
        candidate = current | {beliefs[i]}
        candidate_formulas = [b.formula for b in candidate]
        if entails(candidate_formulas, formula):
            continue  # adding this belief causes entailment; skip

        # candidate does not entail formula — try to extend it
        extended = False
        for j in range(i + 1, len(beliefs)):
            next_candidate = candidate | {beliefs[j]}
            next_formulas = [b.formula for b in next_candidate]
            if not entails(next_formulas, formula):
                # Can still grow — recurse
                _find_remainders(beliefs, formula, candidate, i + 1, results)
                extended = True
                break

        if not extended:
            # Try all further additions — if none can be added, it's maximal
            can_extend = False
            for j in range(len(beliefs)):
                if beliefs[j] in candidate:
                    continue
                next_candidate = candidate | {beliefs[j]}
                next_formulas = [b.formula for b in next_candidate]
                if not entails(next_formulas, formula):
                    can_extend = True
                    break
            if not can_extend:
                # Maximal non-entailing subset found
                if candidate not in results:
                    results.append(candidate)

    # Also check if the current set itself (without adding more) is maximal
    # This handles the case where we've processed all indices
    if start_idx >= len(beliefs) and current:
        current_formulas = [b.formula for b in current]
        if not entails(current_formulas, formula):
            if current not in results:
                results.append(current)


def compute_remainder_sets(beliefs: List[Belief], formula: Formula) -> List[FrozenSet[Belief]]:
    """
    Public function: compute B⊥formula.
    Returns a list of frozensets of Belief objects.
    Each frozenset is a maximal subset of beliefs that does not entail formula.
    """
    if not beliefs:
        return []

    # Check vacuous case first
    formulas = [b.formula for b in beliefs]
    if not entails(formulas, formula):
        return [frozenset(beliefs)]

    # Full computation via generate-and-test
    # We enumerate all subsets of beliefs (excluding full set which entails φ),
    # keep those that don't entail φ, and retain only the maximal ones.
    n = len(beliefs)
    all_non_entailing: List[FrozenSet[Belief]] = []

    for mask in range(1, 1 << n):  # all non-empty subsets
        subset = frozenset(beliefs[i] for i in range(n) if mask & (1 << i))
        subset_formulas = [b.formula for b in subset]
        if not entails(subset_formulas, formula):
            all_non_entailing.append(subset)

    # Keep only maximal ones
    maximal = []
    for s in all_non_entailing:
        if not any(s < t for t in all_non_entailing):
            if s not in maximal:
                maximal.append(s)

    return maximal if maximal else []


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

    beliefs = bb.beliefs  # sorted by priority desc

    # Vacuous check: if B does not entail φ, return B unchanged
    if not entails(bb.formulas, formula):
        result = BeliefBase()
        for b in beliefs:
            result.add(b.formula, b.priority)
        return result

    # Compute remainder sets
    remainders = compute_remainder_sets(beliefs, formula)

    if not remainders:
        # φ is a tautology or base is empty — return empty base
        return BeliefBase()

    # Apply selection function
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
