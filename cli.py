"""
Interactive CLI for the Belief Revision Engine.

Run with:
    python cli.py
"""

import os

from belief_revision import (
    BeliefBase, parse, entails, is_consistent,
    contract, expand, revise,
)
from belief_revision.agm_tests import run_all_tests

# Enable ANSI on Windows
if os.name == "nt":
    os.system("")

# ── ANSI helpers ──────────────────────────────────────────────────────────────
_RST    = "\033[0m"
_BOLD   = "\033[1m"
_DIM    = "\033[2m"
_CYAN   = "\033[96m"
_YELLOW = "\033[93m"
_GREEN  = "\033[92m"
_RED    = "\033[91m"
_BLUE   = "\033[94m"
_GRAY   = "\033[90m"
_WHITE  = "\033[97m"

def _fmt_formula(f) -> str:
    return f"{_CYAN}{f}{_RST}"

def _fmt_priority(p: int) -> str:
    return f"{_YELLOW}{p}{_RST}"

def _fmt_ok(s: str) -> str:
    return f"{_GREEN}{s}{_RST}"

def _fmt_err(s: str) -> str:
    return f"{_RED}{s}{_RST}"

def _fmt_dim(s: str) -> str:
    return f"{_GRAY}{s}{_RST}"

def _fmt_bold(s: str) -> str:
    return f"{_BOLD}{s}{_RST}"

def _sep(char="─", width=52) -> str:
    return _GRAY + char * width + _RST


# ── Display ───────────────────────────────────────────────────────────────────

def _show_bb(bb: BeliefBase) -> None:
    beliefs = bb.beliefs
    if not beliefs:
        print(f"  {_fmt_dim('(belief base is empty)')}")
        return
    print(f"  {_sep()}")
    for b in beliefs:
        bar = "█" * b.priority
        print(f"  {_fmt_priority(b.priority):>6}  {bar:<10}  {_fmt_formula(b.formula)}")
    print(f"  {_sep()}")
    n = len(beliefs)
    consistent = is_consistent(bb.formulas)
    c_str = _fmt_ok("consistent") if consistent else _fmt_err("inconsistent")
    print(f"  {_fmt_dim(f'{n} belief(s),')} {c_str}")


def _show_diff(before: BeliefBase, after: BeliefBase) -> None:
    before_set = {(str(b.formula), b.priority) for b in before.beliefs}
    after_set  = {(str(b.formula), b.priority) for b in after.beliefs}
    removed = before_set - after_set
    added   = after_set  - before_set

    if not removed and not added:
        print(f"  {_fmt_dim('(no change)')}")
        return

    for fs, p in sorted(removed):
        print(f"  {_RED}─{_RST}  [{_fmt_priority(p)}]  {_fmt_formula(fs)}")
    for fs, p in sorted(added):
        print(f"  {_GREEN}+{_RST}  [{_fmt_priority(p)}]  {_fmt_formula(fs)}")


HELP = f"""
{_fmt_bold('Commands:')}
  {_CYAN}add{_RST} <formula> [priority]      Add a belief {_GRAY}(default priority=1){_RST}
  {_CYAN}remove{_RST} <formula>              Remove a belief
  {_CYAN}show{_RST}                          Show current belief base
  {_CYAN}entails{_RST} <formula>             Check if BB |= formula
  {_CYAN}consistent{_RST}                    Check if BB is consistent
  {_CYAN}contract{_RST} <formula>            Contract by formula
  {_CYAN}expand{_RST}  <formula> [priority]  Expand with formula
  {_CYAN}revise{_RST}  <formula> [priority]  Revise by formula  {_GRAY}(Levi Identity){_RST}
  {_CYAN}test{_RST}    <formula>             Run AGM postulate tests
  {_CYAN}reset{_RST}                         Clear the belief base
  {_CYAN}help{_RST}                          Show this help
  {_CYAN}quit{_RST} / {_CYAN}exit{_RST}                   Exit

{_fmt_bold('Formula syntax:')}
  {_CYAN}p, q, r, ...{_RST}    atomic variables
  {_CYAN}~p{_RST}              NOT
  {_CYAN}p & q{_RST}           AND
  {_CYAN}p | q{_RST}           OR
  {_CYAN}p -> q{_RST}          implication
  {_CYAN}p <-> q{_RST}         biconditional
  {_CYAN}(p & q){_RST}         grouping

{_fmt_bold('Example session:')}
  >> add p -> q 3
  >> add p 2
  >> entails q
  >> revise ~p 3
  >> show
"""


def _parse_formula_and_priority(raw: str):
    """
    Split 'p -> q 3' into (formula_str='p -> q', priority=3).
    If the last token is a positive integer, treat it as the priority.
    Otherwise default to priority=1.
    """
    tokens = raw.rsplit(None, 1)
    if len(tokens) == 2 and tokens[1].isdigit():
        return tokens[0].strip(), int(tokens[1])
    return raw.strip(), 1


def run_cli():
    bb = BeliefBase()
    print()
    print(f"  {_fmt_bold('Belief Revision Engine')}  {_GRAY}— Interactive CLI{_RST}")
    print(f"  {_fmt_dim('Type')} {_CYAN}help{_RST} {_fmt_dim('for commands.')}")
    print()

    prompt = f"{_BLUE}▶{_RST} "

    while True:
        try:
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {_fmt_dim('Bye!')}")
            break

        if not line:
            continue

        parts = line.split(None, 1)
        cmd = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""

        if cmd in ("quit", "exit", "q"):
            print(f"  {_fmt_dim('Bye!')}")
            break

        elif cmd == "help":
            print(HELP)

        elif cmd == "show":
            _show_bb(bb)

        elif cmd == "reset":
            bb = BeliefBase()
            print(f"  {_fmt_ok('✓')} Belief base cleared.")

        elif cmd == "consistent":
            result = is_consistent(bb.formulas)
            icon = _fmt_ok("✓ consistent") if result else _fmt_err("✗ inconsistent")
            print(f"  {icon}")

        elif cmd == "add":
            if not rest:
                print(f"  {_fmt_err('Usage:')} add <formula> [priority]")
                continue
            try:
                formula_str, priority = _parse_formula_and_priority(rest)
                f = parse(formula_str)
                bb.add(f, priority=priority)
                print(f"  {_fmt_ok('+')} [{_fmt_priority(priority)}]  {_fmt_formula(f)}")
            except Exception as e:
                print(f"  {_fmt_err(f'Error: {e}')}")

        elif cmd == "remove":
            if not rest:
                print(f"  {_fmt_err('Usage:')} remove <formula>")
                continue
            try:
                f = parse(rest.strip())
                bb.remove(f)
                print(f"  {_fmt_err('─')} {_fmt_formula(f)} {_fmt_dim('removed')}")
            except Exception as e:
                print(f"  {_fmt_err(f'Error: {e}')}")

        elif cmd == "entails":
            if not rest:
                print(f"  {_fmt_err('Usage:')} entails <formula>")
                continue
            try:
                f = parse(rest.strip())
                result = entails(bb.formulas, f)
                arrow = _fmt_ok("⊨  yes") if result else _fmt_err("⊭  no")
                print(f"  BB |= {_fmt_formula(f)}   {arrow}")
            except Exception as e:
                print(f"  {_fmt_err(f'Error: {e}')}")

        elif cmd == "contract":
            if not rest:
                print(f"  {_fmt_err('Usage:')} contract <formula>")
                continue
            try:
                f = parse(rest.strip())
                before = bb
                bb = contract(bb, f)
                print(f"  {_fmt_dim('contract')} {_fmt_formula(f)}")
                _show_diff(before, bb)
                _show_bb(bb)
            except Exception as e:
                print(f"  {_fmt_err(f'Error: {e}')}")

        elif cmd == "expand":
            if not rest:
                print(f"  {_fmt_err('Usage:')} expand <formula> [priority]")
                continue
            try:
                formula_str, priority = _parse_formula_and_priority(rest)
                f = parse(formula_str)
                before = bb
                bb = expand(bb, f, priority=priority)
                print(f"  {_fmt_dim('expand')} {_fmt_formula(f)}  [{_fmt_priority(priority)}]")
                _show_diff(before, bb)
                _show_bb(bb)
            except Exception as e:
                print(f"  {_fmt_err(f'Error: {e}')}")

        elif cmd == "revise":
            if not rest:
                print(f"  {_fmt_err('Usage:')} revise <formula> [priority]")
                continue
            try:
                formula_str, priority = _parse_formula_and_priority(rest)
                f = parse(formula_str)
                before = bb
                bb = revise(bb, f, priority=priority)
                print(f"  {_fmt_dim('revise')} {_fmt_formula(f)}  [{_fmt_priority(priority)}]")
                _show_diff(before, bb)
                _show_bb(bb)
            except Exception as e:
                print(f"  {_fmt_err(f'Error: {e}')}")

        elif cmd == "test":
            if not rest:
                print(f"  {_fmt_err('Usage:')} test <formula>")
                continue
            try:
                f = parse(rest.strip())
                run_all_tests(bb, f)
            except Exception as e:
                print(f"  {_fmt_err(f'Error: {e}')}")

        else:
            print(f"  {_fmt_err(f'Unknown command: {cmd!r}.')} {_fmt_dim('Type')} {_CYAN}help{_RST} {_fmt_dim('for commands.')}")

        print()


if __name__ == "__main__":
    run_cli()
