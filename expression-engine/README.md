# Expression Canonicalization Engine

Milestone 1 of the BoostAI Question Template Engine.

Converts raw mathematical expressions into a deterministic canonical form
and produces a content-addressed SHA-256 hash. Equivalent expressions
always produce identical hashes.

## Project Structure

```
expression-engine/
├── src/
│   ├── tokenizer/        Tokenizer: string → tokens
│   ├── lexer/            Lexer: token validation
│   ├── ast/              AST nodes + visitors
│   ├── parser/           Recursive-descent parser
│   ├── canonicalizer/    AST → canonical AST
│   ├── hashing/          AST → SHA-256 hash
│   └── utilities/        Shared errors
├── tests/                pytest unit tests
├── requirements.txt
└── README.md
```

## Quick Start

```bash
pip install -r requirements.txt
pytest -v

python -c "
from src.hashing import CanonicalHasher
h = CanonicalHasher()
print(h.hash('2x+5'))      # SHA-256 of canonical form
print(h.canonical_string('5+2x'))  # '5 + 2 * x'
"
```

## Supported Grammar

```
expression  → term (("+" | "-") term)*
term        → unary (("*" | "/") unary)*
unary       → "-" unary | primary
primary     → INTEGER | VARIABLE | "(" expression ")"
equation    → expression ("=" expression)?
```

## Canonicalization Rules

1. **Commutative sorting**: constants first, variables alphabetical
2. **Constant folding**: `2+3` → `5`
3. **Multiplication ordering**: constant operand always on the left
4. **Parenthesis unwrapping**: `(x)` → `x`
