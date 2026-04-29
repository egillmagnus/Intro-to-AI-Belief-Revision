"""
Mastermind — Belief Revision Code-Breaker

Run:
    python run_mastermind.py
"""

import sys
import os
from belief_revision.mastermind import MastermindSolver, get_feedback

# Enable ANSI escape codes on Windows terminals
if os.name == "nt":
    os.system("")

# ── Coloured terminal blocks ──────────────────────────────────────────────────

_ANSI_BG = {
    "R": "\033[41m",
    "G": "\033[42m",
    "B": "\033[44m",
    "Y": "\033[43m",
    "P": "\033[45m",
    "O": "\033[48;5;208m",
    "K": "\033[40m",
    "W": "\033[47m",
}
_RST   = "\033[0m"
_WHITE = "\033[97m"
_BLACK = "\033[30m"
_LIGHT = {"Y", "W"}   # use dark text on light backgrounds


def block(letter: str) -> str:
    """A single coloured terminal block with the colour letter inside."""
    bg = _ANSI_BG.get(letter, "")
    if not bg:
        return f"[{letter}]"
    text = _BLACK if letter in _LIGHT else _WHITE
    return f"{bg}{text} {letter} {_RST}"


def render_code(code: tuple, color_names: list) -> str:
    return " ".join(block(color_names[c]) for c in code)


# ── Game modes ────────────────────────────────────────────────────────────────

MODES = [
    {
        "name":        "Mini",
        "desc":        "4 positions, 4 colors  —  256 possible codes",
        "positions":   4,
        "colors":      4,
        "color_names": ["R", "G", "B", "Y"],
    },
    {
        "name":        "Classic",
        "desc":        "4 positions, 6 colors  —  1 296 possible codes",
        "positions":   4,
        "colors":      6,
        "color_names": ["R", "G", "B", "Y", "P", "O"],
    },
    {
        "name":        "Super",
        "desc":        "5 positions, 8 colors  —  32 768 possible codes",
        "positions":   5,
        "colors":      8,
        "color_names": ["R", "G", "B", "Y", "P", "O", "K", "W"],
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def first_guess(mode: dict) -> tuple:
    p, c = mode["positions"], mode["colors"]
    return tuple(i // 2 % c for i in range(p))


def parse_feedback(s: str, positions: int):
    parts = s.strip().split()
    if len(parts) != 2:
        raise ValueError
    b, w = int(parts[0]), int(parts[1])
    if b < 0 or w < 0 or b + w > positions:
        raise ValueError
    return b, w


def parse_secret(s: str, mode: dict) -> tuple:
    color_names = mode["color_names"]
    s = s.strip().upper()
    parts = s.split() if " " in s else list(s)
    if len(parts) != mode["positions"]:
        raise ValueError(f"Expected {mode['positions']} pegs, got {len(parts)}")
    result = []
    for p in parts:
        if p not in color_names:
            raise ValueError(f"Unknown color '{p}'")
        result.append(color_names.index(p))
    return tuple(result)


def feedback_hint(positions: int):
    print("  Feedback format:  <blacks> <whites>")
    print("    blacks = correct color in correct position")
    print("    whites = correct color in wrong position")
    print(f"  Example: '2 1'  means 2 black pegs, 1 white peg")


# ── Main menu ─────────────────────────────────────────────────────────────────

def main_menu():
    print()
    print("=" * 56)
    print("   MASTERMIND  —  Belief Revision Code-Breaker")
    print("=" * 56)
    print()
    print("  Select a game mode:\n")
    for i, m in enumerate(MODES, 1):
        swatch = " ".join(block(c) for c in m["color_names"])
        print(f"    {i}.  {m['name']:<8}  {m['desc']}")
        print(f"             {swatch}")
        print()

    while True:
        raw = input("  Mode [1/2/3]: ").strip()
        if raw in ("1", "2", "3"):
            mode = MODES[int(raw) - 1]
            break
        print("  Please enter 1, 2, or 3.")

    print()
    raw = input("  Auto mode — AI solves against your secret? [Y/n]: ").strip().lower()
    auto = raw in ("", "y", "yes")
    print()
    return mode, auto


# ── Game loops ────────────────────────────────────────────────────────────────

def run_manual(mode: dict):
    positions   = mode["positions"]
    color_names = mode["color_names"]
    guess       = first_guess(mode)

    print(f"  You are the CODE-MAKER. Think of a secret {positions}-peg code.")
    print(f"  Colors:  " + " ".join(block(c) for c in color_names))
    print()
    feedback_hint(positions)
    print()

    solver = MastermindSolver(
        positions=positions, colors=mode["colors"], color_names=color_names
    )
    solver.set_initial_guess(guess)
    turn = 1

    while True:
        print(f"  Turn {turn}")
        print(f"  Guess:      {render_code(guess, color_names)}")
        print(f"  Remaining:  {len(solver.remaining)} candidates")

        while True:
            try:
                raw = input("  Feedback:   ").strip()
                blacks, whites = parse_feedback(raw, positions)
                break
            except (ValueError, IndexError):
                print("  Invalid — enter two numbers, e.g. '2 1'")
                feedback_hint(positions)

        if blacks == positions:
            print()
            print(f"  Solved in {turn} turn(s)!")
            break

        solver.update(guess, (blacks, whites))
        guess = solver.next_guess()
        if guess is None:
            print("  No remaining candidates — check your feedback for mistakes.")
            break

        print()
        turn += 1
        if turn > 20:
            print("  Could not solve in 20 turns.")
            break


def run_auto(mode: dict):
    positions   = mode["positions"]
    color_names = mode["color_names"]

    print(f"  AUTO MODE — Enter your secret and watch the AI crack it.")
    print(f"  Colors:  " + " ".join(block(c) for c in color_names))
    print(f"  Enter a {positions}-peg code, e.g.: {' '.join(color_names[:positions])}")
    print()

    while True:
        try:
            raw = input("  Your secret: ").strip()
            secret = parse_secret(raw, mode)
            break
        except ValueError as e:
            swatch = " ".join(block(c) for c in color_names)
            print(f"  Invalid: {e}. Choose from: {swatch}")

    print()
    print(f"  Secret locked in: {render_code(secret, color_names)}")
    print()

    solver = MastermindSolver(
        positions=positions, colors=mode["colors"], color_names=color_names
    )
    guess = first_guess(mode)
    solver.set_initial_guess(guess)
    turn = 1

    while True:
        blacks, whites = get_feedback(secret, guess)

        print(f"  Turn {turn}")
        print(f"  Guess:      {render_code(guess, color_names)}")
        print(f"  Remaining:  {len(solver.remaining)} candidates")
        print(f"  Feedback:   {blacks} blacks, {whites} whites")

        if blacks == positions:
            print()
            print(f"  Solved in {turn} turn(s)!")
            break

        solver.update(guess, (blacks, whites))
        guess = solver.next_guess()
        if guess is None:
            print("  No remaining candidates — something went wrong.")
            break

        print()
        turn += 1
        if turn > 20:
            print("  Could not solve in 20 turns.")
            break


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    mode, auto = main_menu()
    if auto:
        run_auto(mode)
    else:
        run_manual(mode)


if __name__ == "__main__":
    main()

