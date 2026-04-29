# cnf.py — Converting Formulas to CNF

## What problem does this file solve?

The resolution algorithm (used for logical entailment) only works if all formulas are in a specific standard format called **CNF — Conjunctive Normal Form**. This file converts any formula into CNF.

---

## What is CNF?

CNF is a formula that looks like:

```
(A or B or C)  AND  (D or E)  AND  (F or ~G)  AND  ...
```

In other words: **a big AND of clauses**, where each clause is **a big OR of literals**.

A **literal** is either a variable (`p`) or its negation (`~p`).

### Examples

| Formula | CNF? | Notes |
|---------|------|-------|
| `p & q` | ✓ | Two single-literal clauses |
| `p \| q` | ✓ | One clause with two literals |
| `p -> q` | ✗ | Has implication — must convert first |
| `~(p & q)` | ✗ | Negation not pushed inward |
| `~p \| ~q` | ✓ | This is the CNF of `~(p & q)` |

---

## Why do we need CNF?

The resolution rule only applies to **clauses** (disjunctions of literals). You cannot resolve `p -> q` with `~p` directly. But once both are in CNF, resolution is purely mechanical:

```
Clause 1:  ~p | q       (from p -> q)
Clause 2:  ~q           (negation of q)
Resolve:   ~p           (new clause)
```

---

## The 4 conversion steps

The conversion follows the standard algorithm from the course slides, applied in order:

### Step 1 — Eliminate biconditionals (`<->`)

Replace every `A <-> B` with `(A -> B) & (B -> A)`.

**Why?** The remaining steps only know how to handle `->`, `&`, `|`, `~`. Biconditionals must be removed first.

### Step 2 — Eliminate implications (`->`)

Replace every `A -> B` with `~A | B`.

**Why?** Implication is just shorthand. After this step, the only connectives left are `&`, `|`, and `~`.

**Example:** `p -> q` becomes `~p | q`

### Step 3 — Push negations inward (NNF — Negation Normal Form)

Use De Morgan's laws to push `~` as deep as possible, so it only sits directly on atoms:

- `~(A & B)` → `~A | ~B`
- `~(A | B)` → `~A & ~B`
- `~~A` → `A`

**Why?** Resolution needs literals (`p` or `~p`), not complex negated expressions like `~(p & q)`.

### Step 4 — Distribute OR over AND

Rewrite `(A & B) | C` as `(A | C) & (B | C)`.

**Why?** CNF requires AND on the outside and OR on the inside. After this step, the formula has that shape.

---

## Internal representation

After conversion, CNF is not stored as a tree of objects. Instead it's a **set of sets of strings**:

```python
# p -> q  becomes:
{
  frozenset({"~p", "q"})
}

# p & (q | ~r)  becomes:
{
  frozenset({"p"}),
  frozenset({"q", "~r"})
}
```

### Design decision: why sets of strings instead of Formula objects?

Resolution only cares about **which literals appear in each clause** — it never needs to rebuild the formula tree. Using sets of strings:

- Makes clause lookup O(1) (hash-based)
- Makes resolution trivial — just set operations
- Keeps the entailment code short and fast

Negative literals are represented as `"~p"` (a string starting with `~`) rather than a `Not(Atom("p"))` object. The helper function `negate_literal("p")` returns `"~p"` and vice versa.

---

## Tautological clauses

A clause like `{p, ~p}` is always true (a tautology) — it contributes nothing to reasoning. The code filters these out during conversion.

**Why?** Including tautological clauses would bloat the clause set without any benefit and could confuse the resolution loop.

---

## Key design decisions summary

| Decision | Why |
|----------|-----|
| 4-step pipeline (in fixed order) | Each step has a clear precondition; ordering prevents interference |
| Store clauses as `frozenset[str]` | Enables fast set operations in resolution; hashable for deduplication |
| Filter tautological clauses early | Keeps clause set small and resolution efficient |
| Recurse on formula tree | Natural match for tree-structured data; easy to read and verify |
