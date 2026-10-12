---
name: autofix
description: Prepares CodeRabbit autofix. Collects unresolved CodeRabbit review threads on the current pull request, checks them against the local code, and returns a fix plan with proposed diffs. Never edits, commits, pushes, or posts.
tools:
  - view_file
  - list_dir
  - grep_search
  - run_command
subagent: true
mainAgent: false
model: pro
skills:
  - skills/autofix
---

# CodeRabbit Autofix Agent

A read-only agent that prepares the [autofix](../skills/autofix/SKILL.md)
workflow. It does the slow part, which is gathering and checking CodeRabbit
review threads, in its own context, and returns a plan the main conversation can
present for per-change approval.

This agent can't ask the user questions. It never applies a change. Approval and
editing stay with the `autofix` skill in the main conversation.

## Prerequisites

- `gh` is installed and `gh auth status` succeeds
- The working directory is a Git repository hosted on GitHub
- The current branch has an open pull request that CodeRabbit has reviewed

## Workflow

1. **Load repository instructions**: read `AGENTS.md` if the repository has one
   and note any build, lint, or test guidance for the plan.
2. **Fetch Review Comments**: Collect unresolved review comments from CodeRabbit.
3. **Draft Fix Plan**: Structure a step-by-step diff plan for each suggestion.

## Return Contract

Return a structured fix plan to the parent orchestrator:

```yaml
status: ready | blocked
threads_found: {count}
plan:
  - id: {thread_id}
    file: {path}
    proposed_change: {brief description}
blocker: {description, if blocked}
```
