# Belief Revision Engine

**02180 Intro to AI — DTU, Spring 2026**

A Python implementation of a propositional logic belief revision engine based on the AGM framework.

---

## Project Structure

```
belief_revision/
    __init__.py        Package exports
    formula.py         Propositional logic AST + recursive-descent parser
    cnf.py             CNF conversion (elim biconditionals → implications → NNF → distribute)
    entailment.py      Resolution-based entailment checker (proof by refutation)
    belief_base.py     Belief base data structure (prioritised set of formulas)
    contraction.py     Partial meet contraction (computes B⊥φ + priority selection)
    revision.py        Expansion and Revision (Levi Identity)
    agm_tests.py       AGM postulate test suite (Success, Inclusion, Vacuity, Consistency, Extensionality)
main.py                Demo entry point
```

---

## Running the Demo

```bash
python main.py
```

---

## Supported Formula Syntax

| Syntax    | Meaning          |
|-----------|------------------|
| `p`       | Atomic variable  |
| `~p`      | Negation         |
| `p & q`   | Conjunction (AND)|
| `p \| q`  | Disjunction (OR) |
| `p -> q`  | Implication      |
| `p <-> q` | Biconditional    |
| `(p & q)` | Grouping         |

Operator precedence (lowest → highest): `<->` → `->` → `|` → `&` → `~`

---

## Implementation Overview

### Stage 1 — Belief Base (`belief_base.py`)

A `BeliefBase` holds a set of `Belief` objects, each pairing a `Formula` with an integer **priority** (epistemic entrenchment). Higher priority = more entrenched = less likely to be removed during contraction.

```python
bb = BeliefBase()
bb.add("p -> q", priority=3)
bb.add("p",      priority=2)
```

### Stage 2 — Entailment (`entailment.py`)

Uses **resolution refutation** (as taught in Lecture 10):
- To check `KB |= φ`, negate φ and add to KB
- Convert KB ∧ ¬φ to CNF clauses
- Repeatedly apply resolution until the empty clause is derived (→ entails) or no new clauses emerge (→ does not entail)

```python
entails(bb.formulas, parse("q"))  # True
```

### Stage 3 — Contraction (`contraction.py`)

**Partial meet contraction** (AGM):
1. Compute `B⊥φ` — all maximal subsets of B that do **not** entail φ
2. Apply selection function γ: choose remainder sets with the highest total priority score
3. Return the intersection ∩ γ(B⊥φ)

```python
bb_new = contract(bb, parse("q"))
```

### Stage 4 — Expansion (`revision.py`)

Simply add the new formula to the belief base:

```python
bb_new = expand(bb, parse("~p"), priority=3)
```

### Revision — Levi Identity

```
B * φ = (B ÷ ¬φ) + φ
```

```python
bb_new = revise(bb, parse("~p"), priority=3)
```

---

## AGM Postulate Tests (`agm_tests.py`)

The implementation is verified against the five required postulates:

| Postulate | Statement |
|-----------|-----------|
| **Success** | `B * φ \|= φ` |
| **Inclusion** | `B * φ ⊆ Cn(B ∪ {φ})` |
| **Vacuity** | If `B ⊭ ¬φ`, then `B * φ ≡ B + φ` |
| **Consistency** | `B * φ` is consistent (when φ is not a contradiction) |
| **Extensionality** | If `φ ≡ ψ`, then `B * φ ≡ B * ψ` |

```python
from belief_revision import run_all_tests, BeliefBase, parse

bb = BeliefBase()
bb.add("p -> q", priority=2)
bb.add("p", priority=1)
run_all_tests(bb, parse("~p"))
```

---

## Dependencies

No external logic or SAT packages are used — the entailment checker and CNF converter are implemented from scratch as required by the assignment.

```
Python 3.10+
```

No third-party packages required.
