"""Entry point for running AGM postulate tests without the RuntimeWarning."""
from belief_revision.agm_tests import *  # noqa: F401,F403

from belief_revision.formula import parse
from belief_revision.belief_base import BeliefBase
from belief_revision.agm_tests import run_all_tests

if __name__ == "__main__":
    bb = BeliefBase()
    bb.add(parse("p"), priority=3)
    bb.add(parse("p -> q"), priority=2)
    bb.add(parse("q -> r"), priority=1)

    print("\nDemo: Revising a belief base about rain/umbrellas")
    print("  p        = it is raining")
    print("  p => q   = if raining, take umbrella")
    print("  q => r   = if umbrella, stay dry")
    print()

    run_all_tests(bb, parse("~p"), formula_eq=parse("~p"))

    print()

    bb2 = BeliefBase()
    bb2.add(parse("a"), priority=2)
    bb2.add(parse("b"), priority=1)
    run_all_tests(bb2, parse("c"), formula_eq=parse("~~c"))

    print()

    bb3 = BeliefBase()
    bb3.add(parse("p & q"), priority=2)
    run_all_tests(bb3, parse("~p"), formula_eq=parse("~p"))
