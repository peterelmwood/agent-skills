# Quickstart: validate the deepen-prompt skill

Run from the repo root. `$S` is a new, empty scratch folder outside the repo.

## 1. Content matches the issue (FR-001, FR-002)

```sh
gh issue view 4 --repo peterelmwood/agent-skills --json body > "$S/issue4.json"
# extract the ````markdown fence to $S/extract/SKILL.md (research R1)
cmp deepen-prompt/SKILL.md "$S/extract/SKILL.md"
find deepen-prompt -type f            # only deepen-prompt/SKILL.md (FR-004)
python <skill-creator>/scripts/quick_validate.py deepen-prompt   # "Skill is valid!"
```

## 2. Archive (FR-005, SC-004)

```powershell
[IO.Compression.ZipFile]::CreateFromDirectory("$PWD\deepen-prompt", "$PWD\deepen-prompt.skill", 'Optimal', $true)
```

```sh
python -I -c "
import zipfile, pathlib
z = zipfile.ZipFile('deepen-prompt.skill')
files = [n for n in z.namelist() if not n.endswith('/')]
disk = sorted(p.as_posix() for p in pathlib.Path('deepen-prompt').rglob('*') if p.is_file())
assert files == disk and not any(chr(92) in n for n in z.namelist())
assert all(z.read(n) == open(n, 'rb').read() for n in files)
print('ok')"
```

## 3. README (FR-006, SC-005)

```sh
grep -c 'step-breakdown deepen-prompt ~/.claude/skills/' README.md   # 2
grep -c 'step-breakdown, deepen-prompt "' README.md                  # 1
grep -c 'All seven skills' README.md                                 # 1
grep -c '](deepen-prompt/SKILL.md)' README.md                        # 1
grep -n '^### deepen-prompt' README.md
```

## 4. .gitignore (FR-007)

```sh
mkdir -p deepen-prompt-workspace && git status --short --ignored deepen-prompt-workspace  # "!!"
rmdir deepen-prompt-workspace
```

## 5. Nothing else changed (FR-008, SC-006)

```sh
git diff --stat 002-step-breakdown-skill -- . ':!specs' ':!deepen-prompt' ':!deepen-prompt.skill' ':!README.md' ':!.gitignore'
# empty
```

## 6. Output evals (SC-001)

Run each issue §8 output prompt with the skill and without it, save the replies in
`deepen-prompt-workspace/iteration-N/` (ignored) or outside the repo, and grade against the
§8 assertions.

## 7. Maintainer-only (SC-002, SC-003)

- Review the eval results in skill-creator's `eval-viewer/generate_review.py --benchmark`.
- On macOS/Linux/WSL, from a scratch directory: write the §8 trigger set as an eval-set JSON
  and run `python -m scripts.run_loop --eval-set <file> --skill-path <repo>/deepen-prompt
  --max-iterations 5 --model <model>`; apply `best_description` if held-out accuracy ≥ 80%,
  then rebuild the archive (§2).
- Smoke test: copy the folder to `~/.claude/skills/`, start a new session, try
  "deeper version of this: 'tell me why my nightly ETL got slower'".
