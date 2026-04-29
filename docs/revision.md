# revision.py — Updating Beliefs When New Information Conflicts

## What problem does this file solve?

This is the **main operation** the whole project is built toward: **revision**.

When the agent receives new information that contradicts what it currently believes, it can't just add the new belief (that would make the belief base inconsistent). It needs to:

1. First **remove** whatever is necessary to make room
2. Then **add** the new information

This file implements both the simpler helper operation (expansion) and the full revision operation.

---

## Two operations

### Expansion — `expand(B, φ)`

**What:** Simply add a new formula to the belief base.  
**When to use:** Only when φ does *not* conflict with existing beliefs.

```
B + φ  =  B ∪ {φ}
```

Expansion is trivial — it just adds φ with the given priority. The result may be inconsistent if you're not careful (that's the caller's responsibility).

---

### Revision — `revise(B, φ)`

**What:** Add φ while ensuring the result stays consistent.  
**When to use:** When φ may contradict something already believed.

Revision uses the **Levi Identity** — a formula from AGM theory:

$$B * \varphi = (B \div \neg\varphi) + \varphi$$

In plain English:

> **Step 1:** Contract by ¬φ — remove enough beliefs so that "¬φ is false" is no longer entailed  
> **Step 2:** Expand with φ — add the new information

### Why this order?

Why not just add φ and remove the conflict afterwards? Because after adding φ you might not know *which* old beliefs caused the conflict. The Levi Identity avoids this by always contracting *before* adding.

---

## Worked example

**Belief base:**
```
[3] p -> q   (if rain, ground is wet)
[2] p        (it is raining)
[1] r        (Alice has umbrella)
```

**Revise by:** `~p` (it is NOT raining)

**Step 1 — Contract by `~~p` (i.e., `p`):**  
Remove enough beliefs so the base no longer entails `p`.  
Result: `{p -> q (3), r (1)}` — `p` itself is dropped (lowest priority among those causing entailment)

**Step 2 — Expand with `~p`:**  
Add `~p` with the given priority.  
Result: `{p -> q (3), ~p (new), r (1)}`

**Final base:** consistent, and `~p` is now believed.

---

## Design decision: the Levi Identity vs. direct revision

There are other ways to implement revision (e.g. Grove's sphere systems, lexicographic revision). We use the Levi Identity because:

- It is the **standard AGM construction** — directly implements the theory from the course
- It **reuses contraction** — no new algorithm needed
- It is **provably correct** — satisfies all 8 AGM revision postulates when contraction satisfies the 8 contraction postulates

---

## Design decision: original belief base is never modified

Both `expand()` and `revise()` return a **new** `BeliefBase` object. The original is left unchanged.

This is important because:
- It makes the code easier to reason about (no hidden side effects)
- It allows the AGM tests to compare before/after states
- It matches the mathematical definition (revision is a function from belief states to belief states)

---

## Key design decisions summary

| Decision | Why |
|----------|-----|
| Levi Identity: `B * φ = (B ÷ ¬φ) + φ` | Standard AGM construction; directly uses contraction |
| Expansion as a separate function | Useful independently (vacuity test, adding non-conflicting beliefs) |
| Return new `BeliefBase`, never modify in place | No side effects; easier to test and reason about |
| Priority parameter on expand/revise | Caller controls how entrenched the new belief should be |
