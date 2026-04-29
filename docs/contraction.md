# contraction.py — Removing a Belief Without Adding Anything New

## What problem does this file solve?

Sometimes the agent needs to **stop believing something** — without learning anything new to replace it. For example:

> The agent believes "it is raining" (`p`) and "if rain then wet ground" (`p -> q`), so it believes "the ground is wet" (`q`).  
> Now it wants to stop believing `q` — perhaps its sensor was wrong.

It can't just delete `q` directly, because `q` is still *implied* by `p` and `p -> q`. It needs to remove enough beliefs so that `q` is **no longer entailed**.

But it also shouldn't throw away more than necessary — that would be irrational.

This is the **contraction** problem, and this file implements the standard AGM solution.

---

## The algorithm: Partial Meet Contraction

### Step 1 — Find all "remainder sets" (B⊥φ)

A **remainder set** is a maximal subset of the belief base that does **not** entail φ.

- "Maximal" means: you cannot add any more beliefs back without the set entailing φ again.
- There may be multiple remainder sets — different ways to give up just enough.

**Example:**

Belief base: `{p, p -> q, r -> p}`  
Contracting by: `q`

Both `{p, r -> p}` and `{p -> q, r -> p}` are remainder sets:
- `{p, r -> p}` does not entail `q` (you need `p -> q` to derive it)
- `{p -> q, r -> p}` does not entail `q` (you need `p` to derive it)

### Step 2 — Pick the best remainder sets (selection function γ)

Since there are multiple ways to contract, we need a rule to choose. The **selection function** picks the remainder set(s) that **retain the highest-priority beliefs**.

We score each remainder set by the **sum of its priorities**:

```
{p(2), r->p(2)}     score = 4
{p->q(3), r->p(2)}  score = 5  ← wins!
```

So the agent keeps `{p -> q, r -> p}` — it drops the lower-priority `p` rather than the higher-priority `p -> q`.

### Step 3 — Take the intersection

If multiple remainder sets tie for the highest score, we take their **intersection** — the beliefs that appear in *all* of the selected sets. This is the safest choice: only keep what every best option agrees on.

**Result:** the contracted belief base.

---

## Why "Partial Meet"?

The name comes from the fact that we take the intersection of a **selection** (partial, not all) of the remainder sets. It contrasts with:

- **Full meet contraction**: take the intersection of *all* remainder sets (too aggressive — drops too much)
- **Maxichoice contraction**: pick exactly *one* remainder set (too arbitrary)

Partial meet is the middle ground that satisfies all the AGM contraction postulates.

---

## The vacuous case

If the belief base **doesn't already entail φ**, there's nothing to contract — the agent doesn't believe φ in the first place. In this case the belief base is returned unchanged.

---

## Implementation detail: how remainder sets are found

Finding all remainder sets is computationally expensive — in the worst case we check all $2^n$ subsets of $n$ beliefs.

The code uses a **bitmasking approach**: iterate over all non-empty subsets, keep those that don't entail φ, then filter for maximality (drop any subset that is a strict subset of another non-entailing subset).

### Fast path for unit literals

When φ is a single literal (an atom like `p`, or a negated atom like `~p`), the $2^n$ enumeration is unnecessary. A belief `b` must appear in every remainder set if and only if `{b}` alone does **not** entail φ. This is because:

- Any belief that individually entails φ must be excluded from every remainder set (otherwise the set would entail φ).
- Any belief that does not individually entail φ can always be included in some maximal non-entailing subset.

So contraction by a unit literal reduces to: **remove every belief that individually entails φ**. This runs in $O(n)$ instead of $O(2^n)$, which is critical when the belief base is large (e.g. in Mastermind after many turns).

### Design decision: why enumerate all subsets for complex formulas?

For small belief bases (as in this assignment), this is perfectly fast. The alternative — a smarter recursive algorithm — was also implemented but the exhaustive approach was kept as the public function because:

- It is **easy to verify as correct**
- Its correctness is obvious from the definition
- Belief bases in practice have < 20 beliefs, making $2^{20} \approx 10^6$ subsets at most

---

## Key design decisions summary

| Decision | Why |
|----------|-----|
| Partial meet (not full meet, not maxichoice) | Satisfies all AGM contraction postulates; standard approach |
| Priority-sum as selection function | Keeps the most entrenched beliefs; simple and intuitive |
| Intersection of selected remainder sets | Only keeps beliefs all best options agree on — conservative and safe |
| Vacuous check first | Short-circuits the expensive subset computation when unnecessary |
| Fast path for unit literals | Contraction by a single literal is $O(n)$ — avoids $2^n$ enumeration |
| Bitmask enumeration for complex formulas | Simple, obviously correct; fast enough for small belief bases |
