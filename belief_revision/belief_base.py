"""
Belief Base data structure.

A belief base is a set of propositional formulas, each assigned an integer
priority (epistemic entrenchment order). Higher priority = more entrenched =
less likely to be removed during contraction.

The priority is used as the selection function in partial meet contraction:
we prefer remainder sets that retain the highest-priority beliefs.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Iterable, Optional

from .formula import Formula, parse


@dataclass(order=True)
class Belief:
    """A single belief with its entrenchment priority."""
    priority: int
    formula: Formula = field(compare=False)

    def __str__(self):
        return f"[{self.priority}] {self.formula}"

    def __repr__(self):
        return f"Belief(priority={self.priority}, formula={self.formula!r})"

    def __hash__(self):
        return hash((self.priority, self.formula))

    def __eq__(self, other):
        return isinstance(other, Belief) and self.priority == other.priority and self.formula == other.formula


class BeliefBase:
    """
    A finite belief base: a prioritised set of propositional formulas.

    Priorities are positive integers; higher = more entrenched.
    When no priority is given, the next available integer is used (default=1).
    """

    def __init__(self):
        self._beliefs: List[Belief] = []

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add(self, formula: Formula | str, priority: int = 1) -> None:
        """Add a belief to the base (no-op if formula already present)."""
        if isinstance(formula, str):
            formula = parse(formula)
        # Avoid exact duplicates (same formula + same priority)
        for b in self._beliefs:
            if b.formula == formula:
                return  # already present
        self._beliefs.append(Belief(priority=priority, formula=formula))

    def remove(self, formula: Formula | str) -> None:
        """Remove all beliefs with the given formula."""
        if isinstance(formula, str):
            formula = parse(formula)
        self._beliefs = [b for b in self._beliefs if b.formula != formula]

    def clear(self) -> None:
        self._beliefs.clear()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @property
    def formulas(self) -> List[Formula]:
        """Return all formulas (without priorities)."""
        return [b.formula for b in self._beliefs]

    @property
    def beliefs(self) -> List[Belief]:
        """Return all Belief objects (sorted by priority descending)."""
        return sorted(self._beliefs, key=lambda b: b.priority, reverse=True)

    def __iter__(self):
        return iter(self.formulas)

    def __len__(self):
        return len(self._beliefs)

    def __contains__(self, formula: Formula | str) -> bool:
        if isinstance(formula, str):
            formula = parse(formula)
        return any(b.formula == formula for b in self._beliefs)

    def __bool__(self):
        return bool(self._beliefs)

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self):
        if not self._beliefs:
            return "BeliefBase { }"
        lines = ["BeliefBase {"]
        for b in self.beliefs:
            lines.append(f"  {b}")
        lines.append("}")
        return "\n".join(lines)

    def __repr__(self):
        return str(self)

    # ------------------------------------------------------------------
    # Snapshot / restore (for testing)
    # ------------------------------------------------------------------

    def snapshot(self) -> List[Belief]:
        """Return a copy of the current beliefs list."""
        return list(self._beliefs)

    def restore(self, snapshot: List[Belief]) -> None:
        """Restore from a snapshot."""
        self._beliefs = list(snapshot)

    @classmethod
    def from_snapshot(cls, snapshot: List[Belief]) -> "BeliefBase":
        bb = cls()
        bb._beliefs = list(snapshot)
        return bb
