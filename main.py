from belief_revision import (
    BeliefBase, parse, entails, is_consistent,
    contract, expand, revise,
)

SEP = "-" * 40


def _show_bb(bb: BeliefBase) -> None:
    beliefs = bb.beliefs
    if not beliefs:
        print("  (belief base is empty)")
        return
    print(SEP)
    for b in beliefs:
        print(f"  [{b.priority}]  {b.formula}")
    print(SEP)
    consistent = is_consistent(bb.formulas)
    status = "consistent" if consistent else "inconsistent"
    print(f"  {len(beliefs)} belief(s), {status}")


def _show_diff(before: BeliefBase, after: BeliefBase) -> None:
    before_set = {(str(b.formula), b.priority) for b in before.beliefs}
    after_set  = {(str(b.formula), b.priority) for b in after.beliefs}
    removed = before_set - after_set
    added   = after_set  - before_set

    if not removed and not added:
        print("  (no change)")
        return

    for fs, p in sorted(removed):
        print(f"  - [{p}]  {fs}")
    for fs, p in sorted(added):
        print(f"  + [{p}]  {fs}")


HELP = """\
Commands:
  add <formula> [priority]      Add a belief (default priority=1)
  remove <formula>              Remove a belief
  show                          Show current belief base
  entails <formula>             Check if BB |= formula
  consistent                    Check if BB is consistent
  contract <formula>            Contract by formula
  expand  <formula> [priority]  Expand with formula
  revise  <formula> [priority]  Revise by formula (Levi identity)
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
    # split 'p -> q 3' into formula_str and optional trailing priority
    tokens = raw.rsplit(None, 1)
    if len(tokens) == 2 and tokens[1].isdigit():
        return tokens[0].strip(), int(tokens[1])
    return raw.strip(), 1


def run_cli():
    bb = BeliefBase()
    print()
    print("Belief Revision Engine")
    print("Type 'help' for commands.")
    print()

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
            _show_bb(bb)

        elif cmd == "reset":
            bb = BeliefBase()
            print("Belief base cleared.")

        elif cmd == "consistent":
            result = is_consistent(bb.formulas)
            print("consistent" if result else "inconsistent")

        elif cmd == "add":
            if not rest:
                print("Usage: add <formula> [priority]")
                continue
            try:
                formula_str, priority = _parse_formula_and_priority(rest)
                f = parse(formula_str)
                bb.add(f, priority=priority)
                print(f"  + [{priority}]  {f}")
            except Exception as e:
                print(f"Error: {e}")

        elif cmd == "remove":
            if not rest:
                print("Usage: remove <formula>")
                continue
            try:
                f = parse(rest.strip())
                bb.remove(f)
                print(f"  removed: {f}")
            except Exception as e:
                print(f"Error: {e}")

        elif cmd == "entails":
            if not rest:
                print("Usage: entails <formula>")
                continue
            try:
                f = parse(rest.strip())
                result = entails(bb.formulas, f)
                print(f"  BB |= {f}   {'yes' if result else 'no'}")
            except Exception as e:
                print(f"Error: {e}")

        elif cmd == "contract":
            if not rest:
                print("Usage: contract <formula>")
                continue
            try:
                f = parse(rest.strip())
                before = bb
                bb = contract(bb, f)
                _show_diff(before, bb)
                _show_bb(bb)
            except Exception as e:
                print(f"Error: {e}")

        elif cmd == "expand":
            if not rest:
                print("Usage: expand <formula> [priority]")
                continue
            try:
                formula_str, priority = _parse_formula_and_priority(rest)
                f = parse(formula_str)
                before = bb
                bb = expand(bb, f, priority=priority)
                _show_diff(before, bb)
                _show_bb(bb)
            except Exception as e:
                print(f"Error: {e}")

        elif cmd == "revise":
            if not rest:
                print("Usage: revise <formula> [priority]")
                continue
            try:
                formula_str, priority = _parse_formula_and_priority(rest)
                f = parse(formula_str)
                before = bb
                bb = revise(bb, f, priority=priority)
                _show_diff(before, bb)
                _show_bb(bb)
            except Exception as e:
                print(f"Error: {e}")

        else:
            print(f"Unknown command: {cmd!r}. Type 'help' for commands.")

        print()


if __name__ == "__main__":
    run_cli()
