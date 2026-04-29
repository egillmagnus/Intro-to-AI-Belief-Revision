# belief_base.py — Storing the Agent's Beliefs

## What problem does this file solve?

The agent needs a place to **store its beliefs** — a container that holds all the formulas the agent currently accepts as true, along with information about how confident it is in each one.

This file defines that container: the `BeliefBase`.

---

## What is a Belief Base?

A belief base is simply a **collection of propositional formulas**, where each formula has an associated **priority** (also called entrenchment).

```
BeliefBase {
  [3] p -> q       ← very confident (priority 3)
  [2] p            ← moderately confident (priority 2)
  [1] r            ← weakly held (priority 1)
}
```

The priorities determine what gets removed first when a contradiction must be resolved.

---

## The two classes

### `Belief` — a single belief

A `Belief` wraps one formula and its priority:

```python
Belief(priority=3, formula=Implies(Atom('p'), Atom('q')))
```

It is a simple data container. The `priority` field is used for sorting (higher = more entrenched).

### `BeliefBase` — the full collection

Holds a list of `Belief` objects and provides methods to add, remove, and query them.

---

## Key operations

| Method | What it does |
|--------|-------------|
| `add(formula, priority)` | Add a belief (ignored if already present) |
| `remove(formula)` | Remove a belief by formula |
| `formulas` | Return all formulas as a plain list (used by entailment) |
| `beliefs` | Return all `Belief` objects sorted by priority (descending) |

---

## Design decisions

### Why store priorities alongside formulas?

The AGM framework requires a **selection function** to decide which beliefs to keep when contracting. The most natural way to implement this is to assign each belief a numeric priority that reflects how "entrenched" it is — how reluctant the agent is to give it up.

The alternative (ordering beliefs by their position in the list, or by logical strength) is harder to reason about and control explicitly.

### Why ignore duplicate formulas?

If `p` is already in the belief base, adding `p` again with a different priority would create ambiguity — which priority applies? The simplest and safest policy is: **the first insertion wins**. Duplicate formulas are silently ignored.

### Why sort by priority descending in `beliefs`?

Contraction needs to find remainder sets that **keep the highest-priority beliefs**. Sorting descending means the most important beliefs come first — useful for display and for the selection function in `contraction.py`.

### Why separate `formulas` and `beliefs` properties?

- `formulas` returns plain `Formula` objects — this is what `entailment.py` needs (it only cares about the logic, not priorities)
- `beliefs` returns full `Belief` objects — this is what `contraction.py` needs (it cares about which beliefs to drop based on priority)

Keeping them separate avoids passing unnecessary data around.

---

## Example usage

```python
bb = BeliefBase()
bb.add("p -> q", priority=3)   # "if rain then wet" — highly trusted
bb.add("p",      priority=2)   # "it is raining" — moderately trusted
bb.add("r",      priority=1)   # "Alice has umbrella" — weakly trusted

print(bb.formulas)   # [p -> q, p, r]
print(bb.beliefs)    # [Belief(3, p->q), Belief(2, p), Belief(1, r)]
```

---

## Key design decisions summary

| Decision | Why |
|----------|-----|
| Priority as an integer | Simple, explicit, easy to compare and sum |
| Ignore duplicate formulas | Avoids ambiguity; first insertion wins |
| Separate `formulas` vs `beliefs` | Clean API — entailment only needs formulas, contraction needs priorities |
| Sort descending on `beliefs` | Highest-priority beliefs first, matching contraction logic |
