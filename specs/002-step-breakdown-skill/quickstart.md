# Quickstart: validate the step-breakdown skill

Run from the repo root on branch `002-step-breakdown-skill`. Commands are shown for Git Bash
/ macOS / Linux; on Windows use `python` from PowerShell 7 for the archive build. `$S` is a
scratch directory outside the repo.

## 1. Content matches the issue (FR-001, SC-005 precondition)

Fetch the issue body as JSON and re-extract both files as in [research R1](./research.md):

```bash
gh issue view 3 --json body > "$S/issue3.json"
# extract the ````markdown and ```python fences to $S/extract/ (see research R1)
cmp "$S/extract/SKILL.md"      step-breakdown/SKILL.md
cmp "$S/extract/check_plan.py" step-breakdown/scripts/check_plan.py
```

Expected: no output from either `cmp`. `head -2 step-breakdown/SKILL.md` shows
`name: step-breakdown`. `find step-breakdown -type f` lists exactly the two files.

## 2. Checker on a clean plan (SC-002)

Copy the worked example from `SKILL.md` (the ```` ```markdown ```` block under
"## Worked example") into `$S/example-steps.md`, then:

```bash
python step-breakdown/scripts/check_plan.py "$S/example-steps.md"; echo "exit=$?"
```

Expected: `Steps: 13 · Gates: 1 · Done: 3`, available now `3, 6, 7, 8`, gate `5` waiting,
`OK: no consistency errors.`, `exit=0`.

## 3. Checker on a broken plan (SC-003)

Write `$S/broken-steps.md` containing: an unknown `Needs` ID, a 2-step cycle, a `⇉` line
listing a step together with its dependency, a step with no `Done when` line, and a step at
`~45 min` with no exception. Run the checker.

Expected: `exit=1`; `ERRORS` names the unknown ID, the cycle, the parallel contradiction and
the missing done-check; `WARNINGS` names the 45-minute step.

Write a second file where every step needs an unticked gate. Expected: the
`no step is available right now` error, `exit=1`.

## 4. Usage and encoding (SC-004)

```bash
python step-breakdown/scripts/check_plan.py; echo "exit=$?"                     # usage, exit=2
PYTHONIOENCODING=cp1252 python step-breakdown/scripts/check_plan.py "$S/example-steps.md"; echo "exit=$?"
```

Expected: the second run prints the emoji gate line without `UnicodeEncodeError`, `exit=0`.

## 5. Archive (FR-010, SC-005)

```bash
python -c "import zipfile; z=zipfile.ZipFile('step-breakdown.skill'); \
names=[n for n in z.namelist() if not n.endswith('/')]; print(sorted(names)); \
print(all('\\\\' not in n for n in z.namelist())); \
print(all(z.read(n)==open(n,'rb').read() for n in names))"
```

Expected: `['step-breakdown/SKILL.md', 'step-breakdown/scripts/check_plan.py']`, `True`,
`True`.

## 6. README (FR-011, SC-006)

```bash
grep -c "step-breakdown" README.md          # ≥ 6
grep -n "All six skills" README.md           # 1 hit
grep -n "^### step-breakdown" README.md      # 1 hit
grep -n "cp -r .*step-breakdown" README.md   # Quick start + Updating
grep -n "Copy-Item .*step-breakdown" README.md
```

## 7. Nothing else changed (FR-012, SC-007)

```bash
git diff --stat main -- . ':!specs' ':!step-breakdown' ':!step-breakdown.skill' ':!README.md' ':!.gitignore'
```

Expected: no output.

## 8. Smoke test (SC-001, manual)

Copy `step-breakdown/` to `~/.claude/skills/`, start a fresh Claude Code session in a scratch
directory and ask: "break down moving apartments in 6 weeks". Expected: one
`*-steps.md` file is saved, and running the checker on it reports no errors and at least one
available step.
