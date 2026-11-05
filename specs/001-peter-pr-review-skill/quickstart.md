# Quickstart: Validate the Peter PR Review Skill

Run these from the repo root in Git Bash. `$SRC` is a folder holding the issue #1 attachments,
downloaded with `gh`/`curl` and the nested package unzipped to `$SRC/z2/peter-pr-review/`.

## Prerequisites

- `git`, `unzip`, `sha256sum` (Git Bash ships all three)
- The attachments from https://github.com/peterelmwood/agent-skills/issues/1

## V1. Content is byte-identical to the attachments (FR-001, FR-002, SC-001)

```bash
(cd peter-pr-review && find . -type f | sort | xargs sha256sum) > /tmp/repo.sha
(cd "$SRC/z2/peter-pr-review" && find . -type f | sort | xargs sha256sum) > /tmp/src.sha
diff /tmp/repo.sha /tmp/src.sha && echo "V1 PASS"
```

Expected: no diff, then `V1 PASS`. Six lines in each file (FR-003).

## V2. Archive matches the folder (FR-004, SC-002)

```bash
unzip -Z1 peter-pr-review.skill | grep -v '/$' | sort > /tmp/entries.txt
(cd . && find peter-pr-review -type f | sort) > /tmp/files.txt
diff /tmp/entries.txt /tmp/files.txt && echo "V2a PASS"
unzip -Z1 peter-pr-review.skill | grep -c '\\' | grep -qx 0 && echo "V2b PASS (no backslashes)"
mkdir -p /tmp/ar && unzip -o -q peter-pr-review.skill -d /tmp/ar && diff -r /tmp/ar/peter-pr-review peter-pr-review && echo "V2c PASS"
```

## V3. Front matter and reference paths (FR-005, FR-006, SC-003)

```bash
sed -n '2p' peter-pr-review/SKILL.md | grep -qx 'name: peter-pr-review' && echo "V3a PASS"
grep -o 'references/[a-z-]*\.md' peter-pr-review/SKILL.md | sort -u | while read p; do
  [ -f "peter-pr-review/$p" ] || echo "MISSING $p"; done; echo "V3b done (no MISSING lines = PASS)"
```

## V4. README (FR-007 to FR-010, SC-004)

```bash
grep -q '\[`peter-pr-review`\](peter-pr-review/SKILL.md)' README.md && echo "V4a table PASS"
grep -nE '^(cp -r|Copy-Item) ' README.md | grep -vc peter-pr-review | grep -qx 0 && echo "V4b commands PASS"
grep -q '^### peter-pr-review' README.md && echo "V4c section PASS"
grep -qi 'all four skills' README.md && echo "V4d FAIL: stale count" || echo "V4d PASS"
```

## V5. Existing skills untouched (FR-011, SC-005)

```bash
git diff --stat main -- design-patterns react-anti-patterns bug-report-issue-author \
  feature-request-issue-author '*.skill' ':!peter-pr-review.skill'
```

Expected: empty output.

## V6. Manual install smoke test (User Story 1)

Copy `peter-pr-review/` to `~/.claude/skills/`, start a new Claude Code session, and ask "What
skills do you have available?". `peter-pr-review` should be listed.
