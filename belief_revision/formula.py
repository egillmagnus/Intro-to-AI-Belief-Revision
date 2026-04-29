"""
Propositional logic formula representation and parser.

Supported syntax:
  ~p          negation
  p & q       conjunction (AND)
  p | q       disjunction (OR)
  p -> q      implication
  p <-> q     biconditional
  (p & q)     parentheses for grouping

Operator precedence (lowest to highest):
  <->  ->  |  &  ~
"""

from __future__ import annotations
from typing import FrozenSet, Set


# ---------------------------------------------------------------------------
# Formula AST
# ---------------------------------------------------------------------------

class Formula:
    def __eq__(self, other):
        return type(self) is type(other) and self._key() == other._key()

    def __hash__(self):
        return hash((type(self).__name__, self._key()))

    def __repr__(self):
        return str(self)

    def _key(self):
        raise NotImplementedError

    def atoms(self) -> Set[str]:
        raise NotImplementedError


class Atom(Formula):
    def __init__(self, name: str):
        self.name = name

    def _key(self):
        return self.name

    def __str__(self):
        return self.name

    def atoms(self):
        return {self.name}


class Not(Formula):
    def __init__(self, sub: Formula):
        self.sub = sub

    def _key(self):
        return (self.sub,)

    def __str__(self):
        if isinstance(self.sub, Atom):
            return f"~{self.sub}"
        return f"~({self.sub})"

    def atoms(self):
        return self.sub.atoms()


class And(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def _key(self):
        return (self.left, self.right)

    def __str__(self):
        l = f"({self.left})" if isinstance(self.left, (Or, Implies, Biconditional)) else str(self.left)
        r = f"({self.right})" if isinstance(self.right, (Or, Implies, Biconditional)) else str(self.right)
        return f"{l} & {r}"

    def atoms(self):
        return self.left.atoms() | self.right.atoms()


class Or(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def _key(self):
        return (self.left, self.right)

    def __str__(self):
        l = f"({self.left})" if isinstance(self.left, (Implies, Biconditional)) else str(self.left)
        r = f"({self.right})" if isinstance(self.right, (Implies, Biconditional)) else str(self.right)
        return f"{l} | {r}"

    def atoms(self):
        return self.left.atoms() | self.right.atoms()


class Implies(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def _key(self):
        return (self.left, self.right)

    def __str__(self):
        l = f"({self.left})" if isinstance(self.left, Biconditional) else str(self.left)
        r = f"({self.right})" if isinstance(self.right, Biconditional) else str(self.right)
        return f"{l} -> {r}"

    def atoms(self):
        return self.left.atoms() | self.right.atoms()


class Biconditional(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def _key(self):
        return (self.left, self.right)

    def __str__(self):
        return f"{self.left} <-> {self.right}"

    def atoms(self):
        return self.left.atoms() | self.right.atoms()


# ---------------------------------------------------------------------------
# Parser  (recursive descent)
# ---------------------------------------------------------------------------
# Grammar:
#   expr      ::= biconditional
#   bicond    ::= implication ('<->' implication)*
#   implication ::= disjunction ('->' implication)?   (right-assoc)
#   disjunction ::= conjunction ('|' conjunction)*
#   conjunction ::= negation ('&' negation)*
#   negation  ::= '~' negation | atom
#   atom      ::= NAME | '(' expr ')'

class _Tokenizer:
    def __init__(self, text: str):
        self._tokens = self._tokenize(text)
        self._pos = 0

    @staticmethod
    def _tokenize(text: str):
        tokens = []
        i = 0
        while i < len(text):
            c = text[i]
            if c.isspace():
                i += 1
            elif c == '(':
                tokens.append('('); i += 1
            elif c == ')':
                tokens.append(')'); i += 1
            elif c == '~':
                tokens.append('~'); i += 1
            elif c == '&':
                tokens.append('&'); i += 1
            elif c == '|':
                tokens.append('|'); i += 1
            elif text[i:i+3] == '<->':
                tokens.append('<->'); i += 3
            elif text[i:i+2] == '->':
                tokens.append('->'); i += 2
            elif c.isalnum() or c == '_':
                j = i
                while j < len(text) and (text[j].isalnum() or text[j] == '_'):
                    j += 1
                tokens.append(text[i:j]); i = j
            else:
                raise ValueError(f"Unknown character: {c!r}")
        tokens.append('EOF')
        return tokens

    def peek(self):
        return self._tokens[self._pos]

    def consume(self, expected=None):
        tok = self._tokens[self._pos]
        if expected and tok != expected:
            raise ValueError(f"Expected {expected!r}, got {tok!r}")
        self._pos += 1
        return tok


def parse(text: str) -> Formula:
    tok = _Tokenizer(text)
    result = _parse_biconditional(tok)
    if tok.peek() != 'EOF':
        raise ValueError(f"Unexpected token: {tok.peek()!r}")
    return result


def _parse_biconditional(tok: _Tokenizer) -> Formula:
    left = _parse_implication(tok)
    while tok.peek() == '<->':
        tok.consume('<->')
        right = _parse_implication(tok)
        left = Biconditional(left, right)
    return left


def _parse_implication(tok: _Tokenizer) -> Formula:
    left = _parse_disjunction(tok)
    if tok.peek() == '->':
        tok.consume('->')
        right = _parse_implication(tok)  # right-associative
        return Implies(left, right)
    return left


def _parse_disjunction(tok: _Tokenizer) -> Formula:
    left = _parse_conjunction(tok)
    while tok.peek() == '|':
        tok.consume('|')
        right = _parse_conjunction(tok)
        left = Or(left, right)
    return left


def _parse_conjunction(tok: _Tokenizer) -> Formula:
    left = _parse_negation(tok)
    while tok.peek() == '&':
        tok.consume('&')
        right = _parse_negation(tok)
        left = And(left, right)
    return left


def _parse_negation(tok: _Tokenizer) -> Formula:
    if tok.peek() == '~':
        tok.consume('~')
        sub = _parse_negation(tok)
        return Not(sub)
    return _parse_atom(tok)


def _parse_atom(tok: _Tokenizer) -> Formula:
    t = tok.peek()
    if t == '(':
        tok.consume('(')
        f = _parse_biconditional(tok)
        tok.consume(')')
        return f
    if t not in ('EOF', '~', '&', '|', '->', '<->', '(', ')'):
        tok.consume()
        return Atom(t)
    raise ValueError(f"Unexpected token in atom position: {t!r}")
