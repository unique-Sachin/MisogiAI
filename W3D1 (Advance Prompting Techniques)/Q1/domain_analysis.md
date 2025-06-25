# Domain Analysis – EdTech Math Tutor LLM Agent

_This document captures the problem space, user personas, and task breakdown used to guide prompt engineering and agent design._

## Users

- **Middle-school & high-school students (grades 6-10)** seeking guided, step-by-step math help.
- **Teachers & researchers** evaluating prompt-engineering effectiveness.

## Math Scope

| Grade | Topics |
|-------|--------|
| 6-7 | fractions, decimals, ratios, basic geometry |
| 8 | linear equations, systems, introductory statistics |
| 9 | quadratic equations, factoring, coordinate geometry |
| 10 | trigonometric ratios, probability basics |

## Agent Requirements (condensed)

1. Provide step-by-step solutions.
2. Explain concepts and highlight misconceptions.
3. Offer adaptive hints; ask clarifying questions when input is ambiguous.
4. Always request self-verification before final answer.
5. Gracefully admit uncertainty (`"I don't know"` fallback).

## Prompt-Engineering Considerations

- **Zero-shot** readability vs. hallucination risk.
- **Few-shot** exemplars for reasoning chains.
- **CoT** explicit "let's think step by step" vs. oversharing internal reasoning.
- **Meta-prompt** instructing model to choose its own strategy.

> _Detailed task analysis will be expanded as the project evolves._ 