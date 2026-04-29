"""
Mastermind using Belief Revision.

Classic Mastermind: 4 positions, 4 colors.

Propositional variables:
    p{i}c{c}  =  "position i has color c"
    i in {0,1,2,3},  c in {0,1,2,3}

Belief base structure:
    - Initial guess: the agent's first guess added as weak unit-clause beliefs
    - After each feedback: unit clauses ruling out / confirming (pos, color) pairs
      are added via revise() — ensuring no contradictions ever arise

Background knowledge (at-most/at-least one color per position) is encoded
implicitly through the self.remaining filter rather than as explicit propositional
formulas. Storing it in the belief base would require 28+ high-priority clauses,
making partial-meet contraction (which enumerates 2^n subsets) intractable.

The next guess is taken from self.remaining — the set of codes still consistent
with all feedback received so far — which is always in sync with the belief base.
"""

from __future__ import annotations
import itertools
from typing import Tuple, List, Optional

from .belief_base import BeliefBase
from .formula import parse
from .revision import revise

# ── Game constants ──────────────────────────────────────────────────────────

POSITIONS = 5
COLORS = 8
COLOR_NAMES = ["R", "G", "B", "Y", "P", "O", "K", "W"]  # Red Green Blue Yellow Purple Orange blacK White

Code = Tuple[int, ...]
ALL_CODES: List[Code] = list(itertools.product(range(COLORS), repeat=POSITIONS))


# ── Helpers ─────────────────────────────────────────────────────────────────

def var(pos: int, color: int) -> str:
    """Propositional variable name for 'position pos has color color'."""
    return f"p{pos}c{color}"


def get_feedback(secret: Code, guess: Code) -> Tuple[int, int]:
    """
    Returns (blacks, whites).
      blacks = exact matches (right color, right position)
      whites = right color but wrong position
    """
    blacks = sum(s == g for s, g in zip(secret, guess))
    whites = (
        sum(min(secret.count(c), guess.count(c)) for c in range(COLORS)) - blacks
    )
    return blacks, whites


def format_code(code: Code, color_names: list = None) -> str:
    if color_names is None:
        color_names = COLOR_NAMES
    return " ".join(color_names[c] for c in code)


# ── Solver ───────────────────────────────────────────────────────────────────

class MastermindSolver:
    """
    Belief-revision-based Mastermind code-breaker.

    The belief base tracks what is known about each (position, color) pair.
    After each guess + feedback, unit clauses are derived and added:
      ~p{i}c{c}  if color c is ruled out at position i  (no remaining code has it)
       p{i}c{c}  if color c is confirmed at position i  (all remaining codes have it)

    The next guess is extracted from the belief base by checking which
    colors are still consistent at each position.
    """

    # Priority levels
    BACKGROUND_PRIORITY = 10   # structural rules — never dropped
    CONFIRMED_PRIORITY = 7     # derived certainties — very entrenched
    RULED_OUT_PRIORITY = 5     # ruled-out colors — moderately entrenched
    GUESS_PRIORITY = 3         # initial guess — weakly held

    def __init__(self, positions: int = POSITIONS, colors: int = COLORS,
                 color_names: list = None):
        self.positions = positions
        self.colors = colors
        self.color_names = color_names or COLOR_NAMES[:colors]
        self.bb = BeliefBase()  # unit-clause beliefs only
        self.remaining: List[Code] = list(
            itertools.product(range(self.colors), repeat=self.positions)
        )
        self.history: List[Tuple[Code, Tuple[int, int]]] = []

    # ── Setup ────────────────────────────────────────────────────────────────

    def set_initial_guess(self, guess: Code) -> None:
        """
        Add the initial guess as weak beliefs.
        The base is empty at this point so expand() suffices.
        """
        for i, c in enumerate(guess):
            f = parse(var(i, c))
            self.bb.add(f, priority=self.GUESS_PRIORITY)

    # ── Update ───────────────────────────────────────────────────────────────

    def update(self, guess: Code, feedback: Tuple[int, int], on_progress=None) -> None:
        """
        Process a guess and its feedback:
          1. Filter the remaining possible codes.
          2. Derive unit clause beliefs and update the belief base.

        on_progress: optional callable(step, total) called after each belief update.
        """
        self.history.append((guess, feedback))

        # Step 1: filter
        self.remaining = [
            code for code in self.remaining
            if get_feedback(code, guess) == feedback
        ]

        # Step 2: derive unit clauses and update the belief base via revise().
        # Using revise() (not expand()) for ALL updates ensures contradictions
        # can never arise: if p{i}c{c} is in the base and we learn ~p{i}c{c},
        # revise() contracts out the old belief before adding the new one.
        total_steps = self.positions * self.colors
        step = 0
        for i in range(self.positions):
            colors_at_pos = {code[i] for code in self.remaining}

            for c in range(self.colors):
                if c not in colors_at_pos:
                    # Color c is impossible at position i → revise by ~p{i}c{c}
                    neg = parse(f"~{var(i, c)}")
                    self.bb = revise(self.bb, neg, priority=self.RULED_OUT_PRIORITY)

                elif colors_at_pos == {c}:
                    # Color c is confirmed at position i → revise by p{i}c{c}
                    pos_f = parse(var(i, c))
                    self.bb = revise(self.bb, pos_f, priority=self.CONFIRMED_PRIORITY)

                step += 1
                if on_progress:
                    on_progress(step, total_steps)

    # ── Next guess ───────────────────────────────────────────────────────────

    def next_guess(self) -> Optional[Code]:
        """
        Return the next guess.

        self.remaining is kept in sync with the belief base: every code in
        remaining is consistent with all unit-clause beliefs.  Picking
        remaining[0] is therefore equivalent to reading the guess from the
        belief base while being guaranteed to produce a valid code.
        """
        if not self.remaining:
            return None
        return self.remaining[0]

    # ── Status ───────────────────────────────────────────────────────────────

    def is_solved(self) -> bool:
        return len(self.remaining) == 1

    def unit_clauses(self) -> List[str]:
        """Return the unit clause beliefs (single literal) for display."""
        return [str(f) for f in self.bb.formulas if "|" not in str(f)]

    def __str__(self) -> str:
        return (
            f"Remaining possible codes: {len(self.remaining)}\n"
            f"Known facts from belief base:\n"
            + ("\n".join(f"  {c}" for c in self.unit_clauses()) or "  (none yet)")
        )
