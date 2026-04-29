"""
Resolution-based logical entailment checker.

To check KB |= φ (does the knowledge base KB entail φ):
  1. Negate φ to get ¬φ
  2. Convert KB ∪ {¬φ} to CNF clauses
  3. Apply resolution until:
     - The empty clause {} is derived  => KB |= φ  (refutation found)
     - No new clauses can be derived   => KB ⊭ φ

This is a proof by refutation (reductio ad absurdum), as taught in Lecture 10.

Implementation: iterated pairwise resolution (Robinson 1965).
"""

from __future__ import annotations
from typing import Iterable, Set, FrozenSet

from .formula import Formula, Not
from .cnf import to_cnf, negate_literal, is_tautological_clause, Clause, CNF


# ---------------------------------------------------------------------------
# Core resolution step
# ---------------------------------------------------------------------------

def _resolve(c1: Clause, c2: Clause) -> Set[Clause]:
    """
    Apply one resolution step between two clauses.
    Returns the set of all resolvents (after factoring / removing tautologies).
    """
    resolvents = set()
    for lit in c1:
        neg = negate_literal(lit)
        if neg in c2:
            # Resolve on lit / neg
            new_clause = frozenset((c1 - {lit}) | (c2 - {neg}))
            if not is_tautological_clause(new_clause):
                resolvents.add(new_clause)
    return resolvents


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def entails(kb: Iterable[Formula], formula: Formula) -> bool:
    """
    Return True iff kb |= formula using resolution refutation.

    Parameters
    ----------
    kb      : iterable of Formula objects (the knowledge base / belief base)
    formula : the Formula to test entailment of
    """
    # Build initial clause set: CNF(KB) ∪ CNF(¬formula)
    clauses: Set[Clause] = set()

    for f in kb:
        for clause in to_cnf(f):
            if not is_tautological_clause(clause):
                clauses.add(clause)

    for clause in to_cnf(Not(formula)):
        if not is_tautological_clause(clause):
            clauses.add(clause)

    # If the empty clause is already present, it is trivially unsatisfiable
    if frozenset() in clauses:
        return True

    # Iterated resolution
    while True:
        new_clauses: Set[Clause] = set()
        clause_list = list(clauses)

        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvents = _resolve(clause_list[i], clause_list[j])
                if frozenset() in resolvents:
                    return True  # contradiction derived
                new_clauses |= resolvents

        if new_clauses.issubset(clauses):
            return False  # no new information can be derived

        clauses |= new_clauses


def is_consistent(kb: Iterable[Formula]) -> bool:
    """
    Return True iff the set of formulas is satisfiable (not contradictory).
    Uses resolution: if KB is inconsistent it entails False (⊥).
    """
    kb_list = list(kb)
    if not kb_list:
        return True

    # KB is inconsistent iff its CNF contains a contradiction
    clauses: Set[Clause] = set()
    for f in kb_list:
        for clause in to_cnf(f):
            if not is_tautological_clause(clause):
                clauses.add(clause)

    if frozenset() in clauses:
        return False

    while True:
        new_clauses: Set[Clause] = set()
        clause_list = list(clauses)

        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvents = _resolve(clause_list[i], clause_list[j])
                if frozenset() in resolvents:
                    return False
                new_clauses |= resolvents

        if new_clauses.issubset(clauses):
            return True

        clauses |= new_clauses
