---
description: Start an autonomous Ralph Loop iteration cycle
argument-hint: "[PROMPT] [--max-iterations N] [--completion-promise TEXT]"
---

# /ralph-loop Workflow

<objective>
Execute autonomous iterative development following the Ralph Loop protocol: externalizing state to PRD.md/TODO.md and progress.txt, picking one atomic task, verifying empirically, committing to git, and continuing until completion.
</objective>

<process>

## 1. Parse Arguments

Extract parameters from input:
- **Task/Prompt**: The overarching goal or specific feature set.
- **Max Iterations**: `--max-iterations <N>` (default: unlimited or until task list completed).
- **Completion Promise**: `--completion-promise <TEXT>` (default: `DONE`).

---

## 2. Initialize State Files

Check if tracking files exist. If not, scaffold them:

1. **Task File (`PRD.md` or `TODO.md`)**:
   - Contains breakdown of tasks with checkable items (`- [ ]`).
2. **Progress Log (`progress.txt`)**:
   - Create if missing:
     ```text
     # Ralph Loop Progress Log
     Started: <timestamp>
     Goal: <goal>
     ---
     ```

---

## 3. Execute Single Iteration

In each iteration step:

1. **Read `progress.txt`**: Learn what previous iterations achieved and any known traps/blockers.
2. **Inspect Task List**: Identify the next unchecked `- [ ]` item.
3. **Execute**:
   - Write code, configure files, or perform the requested action.
4. **Empirically Verify**:
   - Run tests, linters, or build scripts. Ensure no regressions.
5. **Mark Completed**:
   - Change the item to `- [x]` in `PRD.md` or `TODO.md`.
6. **Commit**:
   - Stage changes: `git add -A`
   - Commit: `git commit -m "feat(<task>): <description>"`
   - Confirm commit: `git log -1 --oneline`
7. **Record Progress**:
   - Append to `progress.txt`:
     ```text
     [Iteration N] Completed: <Task Name>
     Notes: <What changed, how verified>
     ```

---

## 4. Check Termination Condition

- If all tasks in `PRD.md`/`TODO.md` are marked `- [x]`, or completion condition is met:
  Output:
  ```xml
  <promise>DONE</promise>
  ```
- If max iterations reached, summarize status and pause.
- Otherwise, proceed to the next iteration.

</process>
