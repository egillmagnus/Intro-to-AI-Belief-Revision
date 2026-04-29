# entailment.py — Checking if Beliefs Logically Follow

## What problem does this file solve?

Given a set of beliefs, we need to answer: **"does this new formula logically follow from what we already know?"**

For example:
- Beliefs: `p` (it is raining), `p -> q` (if rain then wet ground)
- Question: does `q` (ground is wet) follow?
- Answer: **yes** — any world where both beliefs are true must also have `q` true.

This file implements a mechanical algorithm to answer that question for any formula.

---

## The core idea: Proof by Contradiction (Refutation)

Instead of proving `KB |= φ` directly, we prove it **by contradiction**:

> "Assume φ is FALSE. Show this leads to a contradiction with KB."
> If a contradiction is found → φ must be true → KB entails φ.

This is called **resolution refutation** — the standard approach taught in the course.

### Step by step

1. Take the knowledge base KB (all current beliefs)
2. Add the **negation** of the formula we want to prove: `¬φ`
3. Convert everything to CNF (sets of clauses)
4. Repeatedly apply the resolution rule
5. If we ever derive the **empty clause `{}`** → contradiction found → `KB |= φ`
6. If no new clauses can be derived → `KB ⊭ φ`

---

## The Resolution Rule

Resolution is a single inference rule that works on two clauses:

```
Clause 1:   A | B | C
Clause 2:  ~B | D | E
                           (B and ~B cancel out)
Result:     A | C | D | E
```

If the two halves cancel completely:
```
Clause 1:   B
Clause 2:  ~B
Result:     {}   (empty clause = contradiction!)
```

### Design decision: why resolution instead of truth tables?

A truth table checks all possible combinations of variable assignments. With $n$ variables that's $2^n$ rows.

Resolution instead works symbolically — it never enumerates all worlds. For the small belief bases in this project both would work, but resolution is:

- The method explicitly required by the assignment
- Scales much better as the number of variables grows
- Directly connected to the formal theory covered in the course

---

## How the loop works

```
Initial clauses = CNF(KB) + CNF(¬φ)

Repeat:
  For every pair of clauses (C1, C2):
    Try to resolve them → get resolvents
    If empty clause found → return True (entails)
  
  If no new clauses were generated → return False (doesn't entail)
  Add new clauses to the set and repeat
```

This is **Robinson's resolution** (1965) — guaranteed to terminate and be complete for propositional logic.

### Design decision: why pairwise resolution over all pairs?

There are more efficient strategies (e.g. unit resolution, set-of-support). We use exhaustive pairwise resolution because:

- It is **complete** — will always find the contradiction if one exists
- It is **simple to implement and verify**
- The belief bases in this project are small, so performance is not a concern

---

## Tautological clauses are filtered out

A clause like `{p, ~p}` is always true and can never contribute to a contradiction. Keeping it would just waste time — so these are removed immediately.

---

## `is_consistent()` — checking for contradictions

A second public function checks whether a set of beliefs is **self-consistent** (i.e., there exists at least one possible world where all beliefs are true at the same time).

It works by running resolution on the beliefs alone (no extra formula). If the empty clause is derived, the beliefs contradict themselves.

This is used by the AGM Consistency postulate test and by contraction to verify the result is valid.

---

## Key design decisions summary

| Decision | Why |
|----------|-----|
| Proof by refutation (add ¬φ, find contradiction) | Standard complete method; matches course material |
| Exhaustive pairwise resolution | Simple, provably complete for propositional logic |
| Filter tautological clauses | Keeps the clause set minimal; they can never produce the empty clause |
| Separate `is_consistent()` function | Needed independently by contraction and AGM tests |
