from __future__ import annotations
from typing import List, FrozenSet
from itertools import combinations

from .formula import Formula, parse
from .belief_base import BeliefBase, Belief
from .entailment import entails


def _compute_remainder_sets(beliefs: List[Belief], formula: Formula) -> List[FrozenSet[Belief]]:
    # enumerate largest-first so maximal subsets are found before smaller ones
    n = len(beliefs)
    remainder_sets: List[FrozenSet[Belief]] = []

    for size in range(n, 0, -1):
        for subset_tuple in combinations(beliefs, size):
            subset = frozenset(subset_tuple)
            subset_formulas = [b.formula for b in subset]

            if entails(subset_formulas, formula):
                continue

            dominated = any(subset < existing for existing in remainder_sets)
            if dominated:
                continue

            remainder_sets.append(subset)

    return remainder_sets


def _priority_score(remainder: FrozenSet[Belief]) -> int:
    return sum(b.priority for b in remainder)


def _select(remainders: List[FrozenSet[Belief]]) -> List[FrozenSet[Belief]]:
    # keep only the highest-scoring remainder sets
    if not remainders:
        return []
    max_score = max(_priority_score(r) for r in remainders)
    return [r for r in remainders if _priority_score(r) == max_score]


def contract(bb: BeliefBase, formula: Formula | str) -> BeliefBase:
    # partial meet contraction; returns a new BeliefBase, original unchanged
    if isinstance(formula, str):
        formula = parse(formula)

    beliefs = bb.beliefs

    if not entails(bb.formulas, formula):
        result = BeliefBase()
        for b in beliefs:
            result.add(b.formula, b.priority)
        return result

    remainders = _compute_remainder_sets(beliefs, formula)

    if not remainders:
        return BeliefBase()

    selected = _select(remainders)

    intersection = selected[0]
    for r in selected[1:]:
        intersection = intersection & r

    result = BeliefBase()
    for b in intersection:
        result.add(b.formula, b.priority)

    return result
