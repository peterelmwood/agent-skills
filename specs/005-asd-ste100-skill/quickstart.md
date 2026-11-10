# Quickstart: validate the asd-ste100 skill

Run from the repo root on branch `005-asd-ste100-skill`. Commands are shown for Git Bash /
macOS / Linux, except the PowerShell 7 archive build. `$S` is a scratch directory outside
the repo.

## 1. Content matches the issue (FR-001, FR-002, SC-001)

```bash
gh issue view 6 --repo peterelmwood/agent-skills --json body > "$S/issue6.json"
# extract the ````markdown and ````yaml fences to $S/extract/ (research R1), then:
cmp "$S/extract/SKILL.md"           asd-ste100/SKILL.md
cmp "$S/extract/agents/openai.yaml" asd-ste100/agents/openai.yaml
python -c "import yaml; t=open('asd-ste100/SKILL.md',encoding='utf-8').read(); print(yaml.safe_load(t.split('---\n')[1])['name'])"
```

Expected: no `cmp` output; `asd-ste100`. `find asd-ste100 -type f` lists exactly the two files.

## 2. Build the archive (FR-006)

```powershell
$skill = 'asd-ste100'
Add-Type -AssemblyName System.IO.Compression.FileSystem
Remove-Item "$skill.skill" -ErrorAction SilentlyContinue
[IO.Compression.ZipFile]::CreateFromDirectory("$PWD\$skill", "$PWD\$skill.skill", 'Optimal', $true)
```

## 3. Check the archive (SC-002)

```bash
python -c "import zipfile; z=zipfile.ZipFile('asd-ste100.skill'); \
names=[n for n in z.namelist() if not n.endswith('/')]; print(sorted(names)); \
print(all('\\\\' not in n for n in z.namelist())); \
print(all(z.read(n)==open(n,'rb').read() for n in names))"
```

Expected: `['asd-ste100/SKILL.md', 'asd-ste100/agents/openai.yaml']`, `True`, `True`.

## 4. README (FR-007, SC-003)

```bash
grep -n "All seven skills" README.md            # 1 hit
grep -n "^### asd-ste100" README.md             # 1 hit
grep -n "cp -r .*asd-ste100" README.md          # Quick start + Updating (2 hits)
grep -n "Copy-Item .*asd-ste100" README.md      # 1 hit
grep -n "(asd-ste100/SKILL.md)" README.md       # table row
```

## 5. Nothing else changed (FR-008, SC-004)

```bash
git diff --stat 002-step-breakdown-skill -- . ':!specs' ':!asd-ste100' ':!asd-ste100.skill' ':!README.md'
```

Expected: no output.

## 6. Smoke test (manual, maintainer)

Copy `asd-ste100/` to `~/.claude/skills/`, start a new Claude Code session and ask "rewrite
this maintenance procedure in Simplified Technical English" with a short procedure. Expected:
an STE-inspired rewrite with verification notes and no compliance claim. Then ask for a
general email rewrite: the skill should not trigger.
