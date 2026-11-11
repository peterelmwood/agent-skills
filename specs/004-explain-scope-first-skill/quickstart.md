# Quickstart: Verify the Explain-Scope-First Skill

Run from the repo root. `$S` is a new, empty scratch folder outside the repo.

## §1 Source matches the issue

```sh
gh issue view 5 --repo peterelmwood/agent-skills --json body --jq .body > $S/issue5.md
python -I -c "import sys; L=open(sys.argv[1],'rb').read().split(b'\n'); i=L.index(b'\`\`\`\`markdown'); j=L.index(b'\`\`\`\`', i+1); open(sys.argv[2],'wb').write(b'\n'.join(L[i+1:j])+b'\n')" $S/issue5.md $S/SKILL.md
git show HEAD:explain-scope-first/SKILL.md > $S/committed.md
cmp $S/SKILL.md $S/committed.md && echo SOURCE_OK
git ls-files explain-scope-first        # only explain-scope-first/SKILL.md
git show HEAD:explain-scope-first/SKILL.md | sed -n '2p'   # name: explain-scope-first
```

## §2 Build the archive (PowerShell 7)

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::CreateFromDirectory("$PWD\explain-scope-first", "$PWD\explain-scope-first.skill", 'Optimal', $true)
```

Build from LF working-tree bytes (the file is written with LF; check `git ls-files --eol`).

## §3 Archive matches committed blobs

```sh
python -I -c "
import zipfile, subprocess
z = zipfile.ZipFile('explain-scope-first.skill')
names = [n for n in z.namelist() if not n.endswith('/')]
print(names, all('\\\\' not in n for n in z.namelist()))
print(all(z.read(n) == subprocess.run(['git','show','HEAD:'+n], capture_output=True).stdout for n in names))
"
```

Expected: `['explain-scope-first/SKILL.md'] True` then `True`.

## §4 README

```sh
grep -c 'asd-ste100 explain-scope-first ~/.claude/skills/' README.md   # 2
grep -c 'asd-ste100, explain-scope-first "' README.md                  # 1
grep -c 'All nine skills' README.md                                    # 1
grep -c '(explain-scope-first/SKILL.md)' README.md                     # 1
grep -n '^### explain-scope-first' README.md                           # after ### asd-ste100, before ## How skills work
```

## §5 Scope check

```sh
git diff --stat skills-step-breakdown-deepen-prompt-asd-ste100 -- . ':!specs' ':!explain-scope-first' ':!explain-scope-first.skill' ':!README.md'
```

Expected: empty.

## §6 Behavioral smoke test (manual, outstanding)

Copy `explain-scope-first/` into `~/.claude/skills/`, start a new Claude Code session, and
run the seven scenarios in issue #5 §8. Inspect operation order and diff excluded files
before/after; don't judge by heading text.
