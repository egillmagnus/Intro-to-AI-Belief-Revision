from __future__ import annotations
from typing import Iterable, Set

from .formula import Formula, Not
from .cnf import to_cnf, negate_literal, is_tautological_clause, Clause


def _resolve(c1: Clause, c2: Clause) -> Set[Clause]:
    resolvents = set()
    for lit in c1:
        neg = negate_literal(lit)
        if neg in c2:
            new_clause = frozenset((c1 - {lit}) | (c2 - {neg}))
            if not is_tautological_clause(new_clause):
                resolvents.add(new_clause)
    return resolvents


def entails(kb: Iterable[Formula], formula: Formula) -> bool:
    # Proof by refutation: KB |= phi  iff  KB + {~phi} is unsatisfiable
    clauses: Set[Clause] = set()

    for f in kb:
        for clause in to_cnf(f):
            if not is_tautological_clause(clause):
                clauses.add(clause)

    for clause in to_cnf(Not(formula)):
        if not is_tautological_clause(clause):
            clauses.add(clause)

    if frozenset() in clauses:
        return True

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
    # KB is consistent iff no contradiction can be derived
    kb_list = list(kb)
    if not kb_list:
        return True

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
