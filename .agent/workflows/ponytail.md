---
description: Toggle Ponytail lazy senior dev mode (simplest code, YAGNI, lean solutions)
argument-hint: "[lite|full|ultra]"
---

# /ponytail Workflow

<objective>
Configure and activate Ponytail mode: solve tasks with the least new code, prioritizing YAGNI, standard libraries, existing codebase patterns, and minimal diffs.
</objective>

<process>

## 1. Parse Mode

Extract level from arguments:
- `lite`: Build what was asked, highlight smaller options in one line.
- `full` (default): Pragmatic senior dev mode (minimum code, zero bloat, stdlib first).
- `ultra`: Push back aggressively on requirements that do not justify their complexity.

## 2. Activate Protocol

Apply the rules defined in `.agents/rules/ponytail.md` and `.agents/skills/ponytail/SKILL.md` for all tasks in this session.

</process>
