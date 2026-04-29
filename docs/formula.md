# formula.py — Representing and Parsing Logic Formulas

## What problem does this file solve?

Before the computer can reason about beliefs, it needs a way to **store and work with logic formulas** like "it is raining" or "if it rains, the ground is wet".

Plain strings like `"p -> q"` are useless for reasoning — you can't do logic on text. So this file converts strings into a structured object called an **AST (Abstract Syntax Tree)** — essentially a tree of nested objects that the rest of the code can work with.

---

## What is an AST?

An AST is a tree where each node is a piece of the formula. For example:

```
"p -> q"  becomes:

    Implies
    /     \
Atom(p)  Atom(q)
```

And `"~(p & q)"` becomes:

```
     Not
      |
     And
    /   \
Atom(p) Atom(q)
```

This tree structure makes it easy to traverse, transform, and reason about formulas recursively.

---

## The 6 node types (classes)

| Class | Symbol | Example | Meaning |
|-------|--------|---------|---------|
| `Atom` | — | `p` | A single propositional variable (true or false) |
| `Not` | `~` | `~p` | Negation — "it is NOT the case that p" |
| `And` | `&` | `p & q` | Conjunction — "p AND q are both true" |
| `Or` | `\|` | `p \| q` | Disjunction — "p OR q (or both) is true" |
| `Implies` | `->` | `p -> q` | Implication — "if p then q" |
| `Biconditional` | `<->` | `p <-> q` | "p if and only if q" |

### Design decision: why classes instead of tuples or strings?

We could have stored formulas as tuples like `("->", "p", "q")`. The reason we use classes instead:

- **Type safety** — you can check `isinstance(f, Implies)` rather than `f[0] == "->"`
- **Equality and hashing work automatically** — we can store formulas in sets and dictionaries, which is essential for CNF conversion and resolution
- **Clean `.atoms()` method** — each node knows how to report which variables it contains, by recursively asking its children

---

## Operator precedence

When you write `"p | q & r"`, does it mean `"(p | q) & r"` or `"p | (q & r)"`? The parser enforces standard logic precedence:

```
lowest priority  →  <->
                    ->
                    |
                    &
highest priority →  ~
```

So `"p | q & r"` is parsed as `"p | (q & r)"` — same as in mathematics.

### Design decision: why a recursive descent parser?

A recursive descent parser is a function that calls itself to handle each level of precedence. It is:

- **Simple to write and read** — each grammar rule maps directly to one function
- **Standard in compilers** — well-understood technique
- **Easy to extend** — adding a new operator (e.g. XOR) just means adding one more level

The alternative (using a parser library like `pyparsing`) was avoided because the assignment says not to use external packages for the core logic.

---

## How parsing works — a quick walkthrough

Input: `"p -> q & r"`

1. Tokenizer splits it into: `['p', '->', 'q', '&', 'r', 'EOF']`
2. Parser starts at the lowest precedence level (`biconditional`)
3. No `<->` found → drops to `implication`
4. Parses left side `p`, sees `->`, parses right side
5. Right side: no `->` → drops to `disjunction` → no `|` → drops to `conjunction`
6. Sees `q & r` → builds `And(Atom('q'), Atom('r'))`
7. Returns `Implies(Atom('p'), And(Atom('q'), Atom('r')))`

---

## Key design decisions summary

| Decision | Why |
|----------|-----|
| Use classes for each connective | Enables `isinstance` checks, clean recursion, hashing |
| Recursive descent parser | Simple, no external dependencies, matches grammar rules directly |
| `_key()` method on each class | Enables structural equality (`p & q == p & q` even if different objects) |
| `atoms()` method on each class | Lets later code (CNF, resolution) find all variables without knowing formula structure |
