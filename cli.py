"""
Interactive CLI for the Belief Revision Engine.

Run with:
    python cli.py
"""

from belief_revision import (
    BeliefBase, parse, entails, is_consistent,
    contract, expand, revise,
)
from belief_revision.agm_tests import run_all_tests

HELP = """
Commands:
  add <formula> [priority]      Add a belief (default priority=1)
  remove <formula>              Remove a belief
  show                          Show current belief base
  entails <formula>             Check if BB |= formula
  consistent                    Check if BB is consistent
  contract <formula>            Contract by formula
  expand  <formula> [priority]  Expand with formula
  revise  <formula> [priority]  Revise by formula  (Levi Identity)
  test    <formula>             Run all 5 AGM postulate tests
  reset                         Clear the belief base
  help                          Show this help
  quit / exit                   Exit

Formula syntax:
  p, q, r, ...    atomic variables
  ~p              NOT
  p & q           AND
  p | q           OR
  p -> q          implication
  p <-> q         biconditional
  (p & q)         grouping

Example session:
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
    print("Belief Revision Engine — Interactive CLI")
    print("Type 'help' for commands.\n")

    while True:
        try:
            line = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not line:
            continue

        parts = line.split(None, 1)
        cmd = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""

        if cmd in ("quit", "exit", "q"):
            print("Bye!")
            break

        elif cmd == "help":
            print(HELP)

        elif cmd == "show":
            if not bb.formulas:
                print("  (belief base is empty)")
            else:
                print(bb)

        elif cmd == "reset":
            bb = BeliefBase()
            print("  Belief base cleared.")

        elif cmd == "consistent":
            result = is_consistent(bb.formulas)
            print(f"  Consistent: {result}")

        elif cmd == "add":
            if not rest:
                print("  Usage: add <formula> [priority]")
                continue
            try:
                formula_str, priority = _parse_formula_and_priority(rest)
                f = parse(formula_str)
                bb.add(f, priority=priority)
                print(f"  Added: [{priority}] {f}")
            except Exception as e:
                print(f"  Error: {e}")

        elif cmd == "remove":
            if not rest:
                print("  Usage: remove <formula>")
                continue
            try:
                f = parse(rest.strip())
                bb.remove(f)
                print(f"  Removed: {f}")
            except Exception as e:
                print(f"  Error: {e}")

        elif cmd == "entails":
            if not rest:
                print("  Usage: entails <formula>")
                continue
            try:
                f = parse(rest.strip())
                result = entails(bb.formulas, f)
                print(f"  BB |= {f}  →  {result}")
            except Exception as e:
                print(f"  Error: {e}")

        elif cmd == "contract":
            if not rest:
                print("  Usage: contract <formula>")
                continue
            try:
                f = parse(rest.strip())
                bb = contract(bb, f)
                print(f"  Contracted by: {f}")
                print(bb if bb.formulas else "  (belief base is now empty)")
            except Exception as e:
                print(f"  Error: {e}")

        elif cmd == "expand":
            if not rest:
                print("  Usage: expand <formula> [priority]")
                continue
            try:
                formula_str, priority = _parse_formula_and_priority(rest)
                f = parse(formula_str)
                bb = expand(bb, f, priority=priority)
                print(f"  Expanded with: [{priority}] {f}")
                print(bb)
            except Exception as e:
                print(f"  Error: {e}")

        elif cmd == "revise":
            if not rest:
                print("  Usage: revise <formula> [priority]")
                continue
            try:
                formula_str, priority = _parse_formula_and_priority(rest)
                f = parse(formula_str)
                bb = revise(bb, f, priority=priority)
                print(f"  Revised by: [{priority}] {f}")
                print(bb if bb.formulas else "  (belief base is now empty)")
            except Exception as e:
                print(f"  Error: {e}")

        elif cmd == "test":
            if not rest:
                print("  Usage: test <formula>")
                continue
            try:
                f = parse(rest.strip())
                run_all_tests(bb, f)
            except Exception as e:
                print(f"  Error: {e}")

        else:
            print(f"  Unknown command: {cmd!r}. Type 'help' for commands.")


if __name__ == "__main__":
    run_cli()
