# Belief Revision Assignment — Action Summary

**Course:** 02180 Intro to AI, SP25  
**Due:** May 4th, 2026 at 23:59  
**Group size:** 4 students  

---

## What to Submit

| # | File | Description |
|---|------|-------------|
| 1 | `report.pdf` | 4–6 page technical report |
| 2 | `declaration.pdf` | Division of labour statement |
| 3 | `source.zip` | All source code + README |

Submission platform: **DTU Learn**

---

## Goal

Build a **Belief Revision Engine** that:
- Holds a set of propositional logic beliefs (a *belief base*)
- Accepts a new propositional formula as input
- Outputs the *revised* belief base according to AGM theory

---

## Core Implementation Stages (Required)

### Stage 1 — Belief Base
- Design and implement a data structure to represent the belief base
- Beliefs are propositional logic formulas in symbolic form (no natural language needed)

### Stage 2 — Logical Entailment Checker
- Implement a method to check whether a formula is logically entailed by the belief base
- Recommended approach: **resolution-based** or CNF + resolution
- **Must be implemented from scratch** — no external logic/SAT packages allowed

### Stage 3 — Contraction
- Implement contraction of the belief base
- Must be based on a **priority order** over formulas in the belief base
- Suggested method: **Partial Meet Contraction** (AGM-compliant)

### Stage 4 — Expansion
- Implement expansion: simply add a new formula to the belief base (if consistent)

**Output:** The resulting new belief base after revision (contraction + expansion = revision)

---

## AGM Postulate Tests (Required)

Your implementation must be tested against these AGM postulates (from Lecture 11):

| Postulate | Description |
|-----------|-------------|
| **Success** | The new formula is in the revised belief base |
| **Inclusion** | Revised base ⊆ original base + new formula |
| **Vacuity** | If ¬φ ∉ K, then K ÷ φ = K |
| **Consistency** | Revised base is consistent (unless φ is a contradiction) |
| **Extensionality** | Logically equivalent inputs yield identical revisions |

---

## Optional: Plausibility Order Approach (Alternative to Stages 1–4)

Instead of the standard approach above, you may implement belief revision on **plausibility orders**:

1. Design a plausibility order over possible worlds
2. Implement logical entailment (truth in all minimal/best states)
3. Implement revision via **lexicographic** or **minimal** change of the order

**Output:** The resulting new plausibility order

---

## Optional Bonus: Mastermind (Extra Credit)

Implement an AI **code-breaker** for the classic Mastermind game using your belief revision engine:

- **Belief base** = background rules of the game + first guess
- On receiving feedback: **revise** the belief base accordingly
- Output the **next guess** derived from the revised belief base
- May reference existing Mastermind strategies and adapt them
- Adds 1 extra page allowance to the report

---

## Report Structure (4–6 pages)

1. **Introduction** — What is belief revision (general) + your specific approach
2. **Stage descriptions** — Follow the stages in Section 2 sequentially
3. **Design choices** — Data structures, formalism choices, justifications
4. **What we learned** — Reflections on the project
5. **Conclusion & Further Work**
6. *(If Mastermind implemented)* — Extra section describing it (1 extra page allowed)

---

## Grading

- **50%** Report quality (precision, use of course concepts, mathematical rigour)
- **50%** Implementation quality (data structures, adherence to logical formalism)

Work through the stages incrementally — partial completion is acceptable and graded accordingly.

---

## Key Technical Concepts to Use

- Propositional Logic (symbolic)
- CNF (Conjunctive Normal Form)
- Resolution
- AGM Revision framework
- Partial Meet Contraction
- (Optional) Plausibility / possible-worlds semantics
