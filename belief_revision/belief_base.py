from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from .formula import Formula, parse


@dataclass(order=True)
class Belief:
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
    # priorities: higher = more entrenched

    def __init__(self):
        self._beliefs: List[Belief] = []

    def add(self, formula: Formula | str, priority: int = 1) -> None:
        # idempotent: skip if formula already present
        if isinstance(formula, str):
            formula = parse(formula)
        for b in self._beliefs:
            if b.formula == formula:
                return
        self._beliefs.append(Belief(priority=priority, formula=formula))

    def remove(self, formula: Formula | str) -> None:
        if isinstance(formula, str):
            formula = parse(formula)
        self._beliefs = [b for b in self._beliefs if b.formula != formula]

    def clear(self) -> None:
        self._beliefs.clear()

    @property
    def formulas(self) -> List[Formula]:
        return [b.formula for b in self._beliefs]

    @property
    def beliefs(self) -> List[Belief]:
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

    def snapshot(self) -> List[Belief]:
        return list(self._beliefs)

    def restore(self, snapshot: List[Belief]) -> None:
        self._beliefs = list(snapshot)

    @classmethod
    def from_snapshot(cls, snapshot: List[Belief]) -> "BeliefBase":
        bb = cls()
        bb._beliefs = list(snapshot)
        return bb
