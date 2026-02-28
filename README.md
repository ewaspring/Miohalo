# Miohalo

**Miohalo** is an experimental language-engineering project for **ASO (Agentic Symbolic Orchestration)**.

It explores one core question:

> Can multiple AI Agents collaborate through a shared “spell-like” symbolic protocol, where writing is computation and symbols are geometry?

---

## Vision

Miohalo treats language as a programmable symbolic field.

Three directions are currently in scope:

1. **Character mutation**: remap/transform Chinese or Japanese characters into a new symbolic layer while preserving machine-operable structure.
2. **Cuneiform-to-26 bridge**: map cuneiform-like symbolic families into a 26-letter operational alphabet for agent interoperability.
3. **Agent spell protocol**: let different AI agents coordinate via compact symbolic “incantations” (ritualized command packets).

In short, Miohalo is not just “new glyphs”; it is a **multi-agent protocol language**.

---

## Core concept: ASO

**ASO = Agentic Symbolic Orchestration**

A minimal ASO loop:

- **Observe**: agent reads symbolic state/context.
- **Transmute**: agent applies glyph/syntax transform rules.
- **Emit Spell**: agent outputs a compact action expression.
- **Resonate**: other agents parse and continue the chain.

This makes symbol transformation and agent collaboration part of the same system.

---

## Current repository structure

- `README.md`: project-level philosophy + roadmap.
- `miohalo-alpha/`: first executable seed of the language module.
  - `scripts/`: data collection, ranking, rendering, and font-audit tooling.
  - `miohalo.config.yaml`: pipeline configuration.

---

## Roadmap (practical)

### Phase A — Symbol inventory
- Build candidate symbol sets (Latin-ext / CJK / Kana / cuneiform-inspired families).
- Score for visual distinctness, composability, and font support.

### Phase B — Mutation grammar
- Define deterministic rewrite grammar:
  - source script → Miohalo glyph class
  - Miohalo glyph class → operational token
- Keep reversible mappings where possible.

### Phase C — Spell packets for agents
- Introduce a tiny message format such as:
  - `invoke`, `bind`, `transform`, `seal`, `handoff`
- Ensure packets can be parsed by heterogeneous AI agents.

### Phase D — Multi-agent runtime
- Build an orchestrator where agents can pass spell packets in sequence.
- Track convergence, divergence, and semantic drift.

---

## Immediate next step

Inside `miohalo-alpha`, we will stabilize:

1. candidate generation,
2. glyph coverage audit,
3. deterministic grouping,
4. and a first draft of the ASO spell schema.

---

## Status

This repository is still a **first seed**, but now with a clearer direction:

- from pure aesthetic philosophy,
- toward a testable **agent collaboration language stack**.

---

## Author
- **Created by:** *Chino (花木智乃)*
- **In collaboration with:** *Yexian (夜弦)*
- **Year:** 2025
