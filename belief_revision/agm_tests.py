"""
AGM Postulate Tests.

Tests that the belief revision implementation satisfies the core AGM postulates
as required by the assignment (Lecture 11).

The five required postulates for revision B * φ:

1. Success       B * φ |= φ
   The new belief φ is in the revised base.

2. Inclusion     B * φ ⊆ Cn(B ∪ {φ})
   Everything in the revised base follows from the original base + new belief.

3. Vacuity       If B ⊭ ¬φ, then B * φ = B + φ
   If φ is consistent with B, revision equals simple expansion.

4. Consistency   B * φ is consistent (unless φ is a contradiction)
   The revised base should not be self-contradictory.

5. Extensionality  If φ ≡ ψ (logically equivalent), then B * φ = B * ψ
   Logically equivalent inputs yield the same revision.

Each test function returns (passed: bool, message: str).
"""

from __future__ import annotations
from typing import Tuple, List

from .formula import Formula, parse, Atom
from .belief_base import BeliefBase
from .entailment import entails, is_consistent
from .revision import revise, expand
from .contraction import contract


TestResult = Tuple[bool, str]


# ---------------------------------------------------------------------------
# Individual postulate checks
# ---------------------------------------------------------------------------

def test_success(bb: BeliefBase, formula: Formula | str) -> TestResult:
    """
    Success postulate: B * φ |= φ
    After revision by φ, the agent believes φ.
    """
    if isinstance(formula, str):
        formula = parse(formula)

    revised = revise(bb, formula)
    passed = entails(revised.formulas, formula)
    msg = (
        "SUCCESS: B * φ |= φ  ✓" if passed
        else "FAIL SUCCESS: Revised base does not entail φ"
    )
    return passed, msg


def test_inclusion(bb: BeliefBase, formula: Formula | str) -> TestResult:
    """
    Inclusion postulate: Every formula in B * φ is entailed by B ∪ {φ}.
    (The revision does not introduce information beyond B + φ.)
    """
    if isinstance(formula, str):
        formula = parse(formula)

    revised = revise(bb, formula)
    combined = list(bb.formulas) + [formula]

    all_included = True
    for f in revised.formulas:
        if not entails(combined, f):
            all_included = False
            break

    msg = (
        "INCLUSION: B * φ ⊆ Cn(B ∪ {φ})  ✓" if all_included
        else "FAIL INCLUSION: Revised base contains formula not in Cn(B ∪ {φ})"
    )
    return all_included, msg


def test_vacuity(bb: BeliefBase, formula: Formula | str) -> TestResult:
    """
    Vacuity postulate: If B ⊭ ¬φ, then B * φ ≡ B + φ.
    If the negation of φ is not entailed by B, revision equals expansion.
    """
    if isinstance(formula, str):
        formula = parse(formula)

    from .formula import Not
    neg_formula = Not(formula)

    # Only check if B does NOT entail ¬φ
    if entails(bb.formulas, neg_formula):
        return True, "VACUITY: Condition not applicable (B |= ¬φ), skipped  ✓"

    revised = revise(bb, formula)
    expanded = expand(bb, formula)

    # Check that revised and expanded entail the same things
    # (they should be semantically equivalent for our purposes)
    # We check mutual entailment of all formulas
    revised_formulas = revised.formulas
    expanded_formulas = expanded.formulas

    # Check both directions
    all_rev_in_exp = all(entails(expanded_formulas, f) for f in revised_formulas)
    all_exp_in_rev = all(entails(revised_formulas, f) for f in expanded_formulas)

    passed = all_rev_in_exp and all_exp_in_rev
    msg = (
        "VACUITY: B * φ ≡ B + φ (when B ⊭ ¬φ)  ✓" if passed
        else "FAIL VACUITY: B * φ ≢ B + φ even though B ⊭ ¬φ"
    )
    return passed, msg


def test_consistency(bb: BeliefBase, formula: Formula | str) -> TestResult:
    """
    Consistency postulate: B * φ is consistent, unless φ itself is a contradiction.
    """
    if isinstance(formula, str):
        formula = parse(formula)

    # If φ is itself inconsistent, we skip
    if not is_consistent([formula]):
        return True, "CONSISTENCY: φ is a contradiction, skipped  ✓"

    revised = revise(bb, formula)
    passed = is_consistent(revised.formulas)
    msg = (
        "CONSISTENCY: B * φ is consistent  ✓" if passed
        else "FAIL CONSISTENCY: B * φ is inconsistent"
    )
    return passed, msg


def test_extensionality(
    bb: BeliefBase,
    formula1: Formula | str,
    formula2: Formula | str,
) -> TestResult:
    """
    Extensionality postulate: If φ ≡ ψ, then B * φ and B * ψ have the same
    logical consequences.
    """
    if isinstance(formula1, str):
        formula1 = parse(formula1)
    if isinstance(formula2, str):
        formula2 = parse(formula2)

    # Check logical equivalence of formula1 and formula2
    phi_entails_psi = entails([formula1], formula2)
    psi_entails_phi = entails([formula2], formula1)

    if not (phi_entails_psi and psi_entails_phi):
        return True, "EXTENSIONALITY: φ ≢ ψ, condition not applicable, skipped  ✓"

    revised1 = revise(bb, formula1)
    revised2 = revise(bb, formula2)

    r1f = revised1.formulas
    r2f = revised2.formulas

    all_r1_in_r2 = all(entails(r2f, f) for f in r1f) if r1f else True
    all_r2_in_r1 = all(entails(r1f, f) for f in r2f) if r2f else True

    passed = all_r1_in_r2 and all_r2_in_r1
    msg = (
        "EXTENSIONALITY: B * φ ≡ B * ψ when φ ≡ ψ  ✓" if passed
        else "FAIL EXTENSIONALITY: B * φ ≢ B * ψ even though φ ≡ ψ"
    )
    return passed, msg


# ---------------------------------------------------------------------------
# Run all postulates as a suite
# ---------------------------------------------------------------------------

def run_all_tests(bb: BeliefBase, formula: Formula | str, formula_eq: Formula | str | None = None) -> None:
    """
    Run all 5 AGM postulate tests and print results.

    Parameters
    ----------
    bb         : the belief base to test against
    formula    : the revision formula φ
    formula_eq : a formula logically equivalent to φ (for extensionality test).
                 If None, extensionality test is skipped.
    """
    if isinstance(formula, str):
        formula = parse(formula)

    print("=" * 60)
    print(f"AGM Postulate Tests  |  Revising by: {formula}")
    print(f"Belief base:\n{bb}")
    print("=" * 60)

    tests: List[TestResult] = [
        test_success(bb, formula),
        test_inclusion(bb, formula),
        test_vacuity(bb, formula),
        test_consistency(bb, formula),
    ]

    if formula_eq is not None:
        tests.append(test_extensionality(bb, formula, formula_eq))
    else:
        tests.append((True, "EXTENSIONALITY: No equivalent formula provided, skipped  ✓"))

    all_passed = True
    for passed, msg in tests:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {msg}")
        if not passed:
            all_passed = False

    print("-" * 60)
    print(f"  Overall: {'ALL TESTS PASSED ✓' if all_passed else 'SOME TESTS FAILED ✗'}")
    print("=" * 60)
    return all_passed


if __name__ == "__main__":
    # -----------------------------------------------------------------------
    # Demo belief base: a simple weather/umbrella scenario
    # -----------------------------------------------------------------------
    bb = BeliefBase()
    bb.add(parse("p"), priority=3)        # p: it is raining
    bb.add(parse("p -> q"), priority=2)   # p -> q: if raining, take umbrella
    bb.add(parse("q -> r"), priority=1)   # q -> r: if umbrella, stay dry

    print("\nDemo: Revising a belief base about rain/umbrellas")
    print("  p        = it is raining")
    print("  p => q   = if raining, take umbrella")
    print("  q => r   = if umbrella, stay dry")
    print()

    # Test 1: Revise by ¬p (it is NOT raining) — conflicts with current belief p
    run_all_tests(bb, parse("~p"), formula_eq=parse("~p"))

    print()

    # Test 2: Revise by a consistent formula (vacuity applies)
    bb2 = BeliefBase()
    bb2.add(parse("a"), priority=2)
    bb2.add(parse("b"), priority=1)
    run_all_tests(bb2, parse("c"), formula_eq=parse("~~c"))  # c ≡ ~~c

    print()

    # Test 3: Revise by a contradiction of existing beliefs
    bb3 = BeliefBase()
    bb3.add(parse("p & q"), priority=2)
    run_all_tests(bb3, parse("~p"), formula_eq=parse("~p"))
