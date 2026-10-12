---
description: Run CodeRabbit AI code review or autofix on changes
argument-hint: "[review|autofix] [--committed|--uncommitted|--dir <path>]"
---

# /coderabbit Workflow

<objective>
Execute CodeRabbit AI code review or autofix across current code changes using the code-review skill and CodeRabbit CLI.
</objective>

<process>

## 1. Parse Arguments

Extract action and options from arguments:
- `review` (default): Review uncommitted or committed changes.
- `autofix`: Apply suggested fixes from review comments.
- Scope options: `--committed`, `--uncommitted`, `--dir <path>`.

---

## 2. Execute Code Review

Activate the `code-review` skill or delegate to the `code-reviewer` subagent:
1. Check authentication status with `coderabbit auth status --agent`.
2. Execute `coderabbit review --agent` (with any requested scope flags).
3. Parse structured findings (critical, major, minor, trivial).
4. Present findings clearly by severity and provide guided remediation.

</process>
