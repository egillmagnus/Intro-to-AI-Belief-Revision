"""
CNF (Conjunctive Normal Form) conversion.

A CNF formula is represented as a frozenset of clauses.
A clause is a frozenset of literals.
A literal is a string: 'p' for positive atom p, '~p' for its negation.

Conversion steps (from the course slides):
  1. Eliminate biconditionals:  A <-> B  =>  (A -> B) & (B -> A)
  2. Eliminate implications:    A -> B   =>  ~A | B
  3. Push negation inward using De Morgan's laws + double negation elimination
  4. Distribute OR over AND (to get CNF)
"""

from __future__ import annotations
from typing import FrozenSet, Set
from .formula import Formula, Atom, Not, And, Or, Implies, Biconditional

Clause = FrozenSet[str]
CNF = FrozenSet[Clause]


# ---------------------------------------------------------------------------
# Step helpers
# ---------------------------------------------------------------------------

def _elim_biconditional(f: Formula) -> Formula:
    """Recursively eliminate all <->."""
    if isinstance(f, Atom):
        return f
    if isinstance(f, Not):
        return Not(_elim_biconditional(f.sub))
    if isinstance(f, And):
        return And(_elim_biconditional(f.left), _elim_biconditional(f.right))
    if isinstance(f, Or):
        return Or(_elim_biconditional(f.left), _elim_biconditional(f.right))
    if isinstance(f, Implies):
        return Implies(_elim_biconditional(f.left), _elim_biconditional(f.right))
    if isinstance(f, Biconditional):
        l = _elim_biconditional(f.left)
        r = _elim_biconditional(f.right)
        return And(Implies(l, r), Implies(r, l))
    raise TypeError(f"Unknown formula type: {type(f)}")


def _elim_implication(f: Formula) -> Formula:
    """Recursively eliminate all ->."""
    if isinstance(f, Atom):
        return f
    if isinstance(f, Not):
        return Not(_elim_implication(f.sub))
    if isinstance(f, And):
        return And(_elim_implication(f.left), _elim_implication(f.right))
    if isinstance(f, Or):
        return Or(_elim_implication(f.left), _elim_implication(f.right))
    if isinstance(f, Implies):
        l = _elim_implication(f.left)
        r = _elim_implication(f.right)
        return Or(Not(l), r)
    raise TypeError(f"Unexpected Biconditional in _elim_implication; call _elim_biconditional first")


def _push_negation_inward(f: Formula) -> Formula:
    """Push all ~ to be directly over atoms (NNF)."""
    if isinstance(f, Atom):
        return f
    if isinstance(f, Not):
        sub = f.sub
        if isinstance(sub, Atom):
            return f  # ~atom stays
        if isinstance(sub, Not):
            # ~~A => A
            return _push_negation_inward(sub.sub)
        if isinstance(sub, And):
            # ~(A & B) => (~A | ~B)
            return Or(_push_negation_inward(Not(sub.left)),
                      _push_negation_inward(Not(sub.right)))
        if isinstance(sub, Or):
            # ~(A | B) => (~A & ~B)
            return And(_push_negation_inward(Not(sub.left)),
                       _push_negation_inward(Not(sub.right)))
        raise TypeError(f"Unexpected node under Not: {type(sub)}")
    if isinstance(f, And):
        return And(_push_negation_inward(f.left), _push_negation_inward(f.right))
    if isinstance(f, Or):
        return Or(_push_negation_inward(f.left), _push_negation_inward(f.right))
    raise TypeError(f"Unexpected node in NNF: {type(f)}")


def _distribute_or_over_and(f: Formula) -> Formula:
    """Convert NNF formula to CNF by distributing | over &."""
    if isinstance(f, Atom) or isinstance(f, Not):
        return f
    if isinstance(f, And):
        return And(_distribute_or_over_and(f.left), _distribute_or_over_and(f.right))
    if isinstance(f, Or):
        left = _distribute_or_over_and(f.left)
        right = _distribute_or_over_and(f.right)
        # (A & B) | C => (A | C) & (B | C)
        if isinstance(left, And):
            return And(_distribute_or_over_and(Or(left.left, right)),
                       _distribute_or_over_and(Or(left.right, right)))
        # A | (B & C) => (A | B) & (A | C)
        if isinstance(right, And):
            return And(_distribute_or_over_and(Or(left, right.left)),
                       _distribute_or_over_and(Or(left, right.right)))
        return Or(left, right)
    raise TypeError(f"Unexpected node in CNF distribution: {type(f)}")


# ---------------------------------------------------------------------------
# Extract clauses from a CNF formula tree
# ---------------------------------------------------------------------------

def _to_literal(f: Formula) -> str:
    """Convert an atom or ~atom to a literal string."""
    if isinstance(f, Atom):
        return f.name
    if isinstance(f, Not) and isinstance(f.sub, Atom):
        return f"~{f.sub.name}"
    raise ValueError(f"Expected literal, got: {f}")


def _collect_disjuncts(f: Formula) -> Set[str]:
    """Collect all literals from a disjunction (one clause)."""
    if isinstance(f, Or):
        return _collect_disjuncts(f.left) | _collect_disjuncts(f.right)
    return {_to_literal(f)}


def _collect_clauses(f: Formula) -> CNF:
    """Collect all clauses from a conjunction of clauses."""
    if isinstance(f, And):
        return _collect_clauses(f.left) | _collect_clauses(f.right)
    # Must be a single clause (disjunction of literals or a literal)
    return frozenset([frozenset(_collect_disjuncts(f))])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def to_cnf(f: Formula) -> CNF:
    """
    Convert a propositional formula to CNF.
    Returns a frozenset of clauses, each clause a frozenset of literal strings.
    An empty frozenset of clauses means the formula is a tautology (True).
    A clause that is an empty frozenset means it is unsatisfiable (False).
    """
    f = _elim_biconditional(f)
    f = _elim_implication(f)
    f = _push_negation_inward(f)
    f = _distribute_or_over_and(f)
    return _collect_clauses(f)


def negate_literal(lit: str) -> str:
    """Return the negation of a literal string."""
    if lit.startswith('~'):
        return lit[1:]
    return f"~{lit}"


def is_tautological_clause(clause: Clause) -> bool:
    """A clause is a tautology if it contains both p and ~p for some p."""
    for lit in clause:
        if negate_literal(lit) in clause:
            return True
    return False
