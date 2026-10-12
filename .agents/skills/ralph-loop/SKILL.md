---
name: ralph-loop
description: Guides and enforces the Ralph Loop autonomous development methodology — externalizing memory to files, iterative task execution, atomic git commits, and verifiable completion promises.
---

# Ralph Loop — Autonomous Iterative Development Skill

> **"Externalize memory to files, run iterative loops with fresh context."**
> 
> The Ralph Loop (popularized by Geoffrey Huntley) enables autonomous, long-running agent execution without context rot or continuous manual supervision.

---

## Core Protocol

```
1. READ TASK LIST     → Inspect PRD.md or TODO.md for pending work
2. CHECK PROGRESS     → Read progress.txt to learn what previous iterations completed
3. SELECT ONE TASK    → Choose exactly ONE uncompleted task (do not batch)
4. IMPLEMENT & VERIFY → Implement the change, run builds/tests/linters empirically
5. COMMIT WORK        → Stage files and commit: `type(scope): description`
6. APPEND PROGRESS    → Append iteration outcome and notes to progress.txt (never delete)
7. CHECK COMPLETION   → If all tasks are done, emit `<promise>DONE</promise>` or stop phrase
```

---

## Key Rules

1. **One Task Per Turn:** Do not attempt multiple features in a single iteration. Keeping tasks atomic ensures clean git history and prevents context bloat.
2. **Append-Only Progress:** Never overwrite or clear `progress.txt`. The log acts as the external memory bridge across iterations.
3. **Empirical Verification:** Always verify with test/build commands before committing. Never assume code works without output proof.
4. **Clean Commits:** Every task must end with a clean git commit. Confirm with `git log -1 --oneline`.
5. **Completion Promises:** When the loop criteria are met or all tasks in the list are checked off, output:
   ```xml
   <promise>DONE</promise>
   ```

---

## File Structure

| File | Purpose |
| :--- | :--- |
| `PRD.md` or `TODO.md` | Task list with checkboxes (`- [ ]` / `- [x]`) |
| `progress.txt` | Append-only log of completed iterations and gotchas |
| `.agent/workflows/ralph-loop.md` | Slash command to start Ralph Loop sessions |
| `scripts/ralph-loop.ps1` / `.sh` | Command-line loop orchestrator |

---

## Integration with Antigravity

- Can be triggered directly in chat via `/ralph-loop`.
- Complements GSD (`SPEC.md` / `PLAN.md`) by providing unattended task-by-task execution cycles.
- Compatible with the VS Code extension `abhishekbhakat.ralph-loop-for-antigravity`.
