"""
Belief Revision Engine — Demo / Entry Point

Demonstrates all four stages of the assignment:
  1. Belief Base
  2. Logical Entailment (resolution)
  3. Contraction (partial meet)
  4. Expansion
  + Revision (Levi Identity)
  + AGM Postulate verification
"""

from belief_revision import (
    BeliefBase, parse,
    entails, is_consistent,
    contract, expand, revise,
    run_all_tests,
)


def separator(title: str = ""):
    print()
    if title:
        print(f"{'─' * 20}  {title}  {'─' * 20}")
    else:
        print("─" * 60)


def main():
    print("=" * 60)
    print("  Belief Revision Engine")
    print("  02180 Intro to AI — DTU, 2026")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Stage 1: Build a Belief Base
    # ---------------------------------------------------------------
    separator("STAGE 1 — Belief Base")

    bb = BeliefBase()
    # p: "It is raining"
    # q: "The ground is wet"
    # r: "Alice brings an umbrella"
    # Beliefs with priorities (higher = more entrenched)
    bb.add("p -> q", priority=3)   # If it rains, the ground is wet
    bb.add("p",      priority=2)   # It is raining
    bb.add("r -> p", priority=2)   # If Alice brings an umbrella, it rains
    bb.add("r",      priority=1)   # Alice brings an umbrella

    print(bb)

    # ---------------------------------------------------------------
    # Stage 2: Logical Entailment
    # ---------------------------------------------------------------
    separator("STAGE 2 — Entailment (Resolution)")

    queries = [
        ("q",       True,  "The ground is wet (derived via p and p->q)"),
        ("~p",      False, "It is NOT raining (contradicts p)"),
        ("r -> q",  True,  "If Alice brings umbrella then ground is wet"),
        ("p & q",   True,  "It rains AND ground is wet"),
        ("p | ~p",  True,  "Tautology"),
    ]

    for formula_str, expected, description in queries:
        formula = parse(formula_str)
        result = entails(bb.formulas, formula)
        status = "✓" if result == expected else "✗ (unexpected)"
        print(f"  BB |= {formula_str:<15}  →  {str(result):<6}  {status}  # {description}")

    # ---------------------------------------------------------------
    # Stage 3: Contraction
    # ---------------------------------------------------------------
    separator("STAGE 3 — Contraction  (Partial Meet)")

    print("Before contraction:")
    print(bb)

    # Contract by 'q' — we no longer want to believe the ground is wet
    print("\nContracting by: q  (ground is wet)")
    bb_contracted = contract(bb, parse("q"))
    print("\nAfter contraction by q:")
    print(bb_contracted)
    print(f"\n  Still entails q?  {entails(bb_contracted.formulas, parse('q'))}")

    # ---------------------------------------------------------------
    # Stage 4: Expansion
    # ---------------------------------------------------------------
    separator("STAGE 4 — Expansion")

    print("Before expansion:")
    print(bb_contracted)

    # Add a new belief: ~p (it is NOT raining)
    print("\nExpanding with: ~p  (it is not raining),  priority=3")
    bb_expanded = expand(bb_contracted, parse("~p"), priority=3)
    print("\nAfter expansion:")
    print(bb_expanded)
    print(f"\n  Consistent?  {is_consistent(bb_expanded.formulas)}")

    # ---------------------------------------------------------------
    # Full Revision (Levi Identity)
    # ---------------------------------------------------------------
    separator("FULL REVISION  (Levi Identity: B * φ = (B ÷ ¬φ) + φ)")

    print("Original belief base:")
    print(bb)
    print("\nRevising by: ~p  (it is NOT raining)")
    bb_revised = revise(bb, parse("~p"), priority=3)
    print("\nRevised belief base:")
    print(bb_revised)
    print(f"\n  Entails ~p?   {entails(bb_revised.formulas, parse('~p'))}")
    print(f"  Consistent?   {is_consistent(bb_revised.formulas)}")

    # ---------------------------------------------------------------
    # AGM Postulate Tests
    # ---------------------------------------------------------------
    separator("AGM POSTULATE TESTS")

    # Test with original bb, revising by ~p
    # Equivalent formula: ~~p <-> ~p? No — use a syntactically different but
    # logically equivalent formula: ~p <-> (p -> False)
    # We'll use: ~~(~p) which should be equivalent to ~p
    run_all_tests(bb, parse("~p"), formula_eq=parse("~(~~p)"))

    separator()
    print("Additional test — revision by a formula consistent with the base:")
    bb2 = BeliefBase()
    bb2.add("a -> b", priority=2)
    bb2.add("b -> c", priority=2)
    run_all_tests(bb2, parse("a"))


if __name__ == "__main__":
    main()
