"""Consistency check for a step-breakdown checklist.

Usage: python check_plan.py <path-to-steps.md>

Checks unique IDs, Needs references, dependency cycles, parallel-line independence,
done-checks, parent/child structure and time estimates. Prints the approximate
active effort and the steps available right now. Exits 1 if any errors are found.
"""
import re
import sys
from pathlib import Path

STEP = re.compile(r"^(\s*)[-*] \[([ xX])\] \*\*(\d+[a-z]?)\.\s+(.+?)\*\*(.*)$")
NEEDS = re.compile(r"Needs:\s*(.*)$")
ID = re.compile(r"^\d+[a-z]?$")
EST = re.compile(r"~\s*(\d+(?:\.\d+)?)\s*(?:[–-]\s*(\d+(?:\.\d+)?))?\s*(min|h)\b", re.I)
PARALLEL = re.compile(r"^>\s*⇉.*?parallel:\s*([0-9a-z ,]+)", re.I)


def parse(text):
    steps, parallels = {}, []
    errors, warnings = [], []
    order = []
    current = None
    for lineno, line in enumerate(text.splitlines(), 1):
        m = STEP.match(line)
        if m:
            indent, mark, sid, title, rest = m.groups()
            if sid in steps:
                errors.append(f"line {lineno}: duplicate ID {sid}")
            nm = NEEDS.search(rest)
            needs = []
            if nm is None:
                errors.append(f"step {sid}: no 'Needs:' field")
            else:
                for tok in re.split(r"[,\s]+", nm.group(1).strip()):
                    tok = tok.strip("*·")
                    if not tok or tok in {"—", "-", "none"}:
                        continue
                    if ID.match(tok):
                        needs.append(tok)
                    else:
                        errors.append(f"step {sid}: unreadable Needs entry '{tok}' (list exact IDs, no ranges)")
            current = steps[sid] = {
                "id": sid, "title": title, "rest": rest, "done": mark.lower() == "x",
                "needs": needs, "gate": "GATE" in title.upper(),
                "parent": "parent" in rest.lower(), "expand": "🔭" in rest or "🔭" in title,
                "has_check": False, "line": lineno,
            }
            order.append(sid)
            continue
        if current is not None and re.search(r"done when", line, re.I):
            current["has_check"] = True
        if line.startswith("#"):
            current = None
        pm = PARALLEL.match(line)
        if pm:
            ids = [t for t in re.split(r"[,\s]+", pm.group(1)) if ID.match(t)]
            parallels.append((lineno, ids, "⚠" in line))
    return steps, order, parallels, errors, warnings


def children_of(steps, sid):
    return [c for c in steps if re.fullmatch(rf"{re.escape(sid)}[a-z]", c)]


def ancestors(steps, sid, memo):
    """All IDs a step transitively depends on (including through its parent)."""
    if sid in memo:
        return memo[sid]
    memo[sid] = set()  # guard against cycles
    result = set()
    for n in steps[sid]["needs"]:
        if n in steps:
            result.add(n)
            result |= ancestors(steps, n, memo)
    memo[sid] = result
    return result


def find_cycle(steps):
    WHITE, GREY, BLACK = 0, 1, 2
    color = {s: WHITE for s in steps}
    stack = []

    def visit(s):
        color[s] = GREY
        stack.append(s)
        for n in steps[s]["needs"]:
            if n not in steps:
                continue
            if color[n] == GREY:
                return stack[stack.index(n):] + [n]
            if color[n] == WHITE:
                cyc = visit(n)
                if cyc:
                    return cyc
        stack.pop()
        color[s] = BLACK
        return None

    for s in steps:
        if color[s] == WHITE:
            cyc = visit(s)
            if cyc:
                return cyc
    return None


def minutes(rest):
    m = EST.search(rest)
    if not m:
        return None
    hi = float(m.group(2) or m.group(1))
    return hi * 60 if m.group(3).lower() == "h" else hi


def main(path):
    text = Path(path).read_text(encoding="utf-8")
    steps, order, parallels, errors, warnings = parse(text)
    if not steps:
        print("ERROR: no steps found (expected lines like '- [ ] **1. Title** · ~15 min · Needs: —')")
        return 1

    for s in steps.values():
        for n in s["needs"]:
            if n not in steps:
                errors.append(f"step {s['id']}: Needs unknown ID {n}")
        if not s["has_check"]:
            errors.append(f"step {s['id']}: no 'Done when' check")
        kids = children_of(steps, s["id"])
        if s["parent"] and not kids:
            errors.append(f"step {s['id']}: marked parent but has no children ({s['id']}a, …)")
        if kids and not s["parent"]:
            warnings.append(f"step {s['id']}: has children but isn't marked 'parent — done when …'")
        if s["parent"] and s["done"] and not all(steps[k]["done"] for k in kids):
            errors.append(f"step {s['id']}: parent ticked but not all children are")
        if s["parent"] and kids and all(steps[k]["done"] for k in kids) and not s["done"]:
            warnings.append(f"step {s['id']}: all children ticked — tick the parent")
        if not (s["gate"] or s["parent"] or s["expand"]):
            m = minutes(s["rest"])
            if m is None:
                warnings.append(f"step {s['id']}: no '~N min' estimate")
            elif m > 30 and "exception" not in s["rest"].lower():
                warnings.append(f"step {s['id']}: ~{m:g} min with no '⚠ exception: <why>'")
        if s["done"]:
            blocked = [n for n in s["needs"] if n in steps and not steps[n]["done"]]
            if blocked:
                warnings.append(f"step {s['id']}: ticked while its Needs {blocked} aren't — check for a conflict")

    cyc = find_cycle(steps)
    if cyc:
        errors.append("dependency cycle: " + " -> ".join(cyc))

    memo = {}
    for lineno, ids, flagged in parallels:
        for i in ids:
            if i not in steps:
                errors.append(f"line {lineno}: parallel line lists unknown ID {i}")
        known = [i for i in ids if i in steps]
        for a in known:
            for b in known:
                if a != b and b in ancestors(steps, a, memo):
                    errors.append(f"line {lineno}: parallel line lists {a} and {b}, but {a} depends on {b}")

    # Totals and availability (parents, gates and 🔭 placeholders carry no active time of their own)
    total = sum(minutes(s["rest"]) or 0 for s in steps.values()
                if not (s["gate"] or s["parent"] or s["expand"]))
    gates = [s for s in steps.values() if s["gate"]]

    def satisfied(n):
        st = steps.get(n)
        if st is None:
            return False
        kids = children_of(steps, n)
        return st["done"] or (st["parent"] and kids and all(steps[k]["done"] for k in kids))

    available = [s for s in (steps[i] for i in order)
                 if not s["done"] and not s["gate"] and not s["parent"]
                 and all(satisfied(n) for n in s["needs"])]
    open_gates = [g for g in gates if not g["done"] and all(satisfied(n) for n in g["needs"])]

    if not available and not all(s["done"] for s in steps.values()):
        errors.append("no step is available right now — the user can't start anything")

    print(f"Steps: {len(steps) - len(gates)} · Gates: {len(gates)} · "
          f"Done: {sum(s['done'] for s in steps.values())} · Active effort: ~{total / 60:.1f} h")
    print("\nAvailable now:")
    for s in available:
        print(f"  {s['id']}. {s['title']}")
    if open_gates:
        print("\nWaiting on (gate prerequisites done, event pending):")
        for g in open_gates:
            print(f"  {g['id']}. {g['title']}")
    for label, items in (("ERRORS", errors), ("WARNINGS", warnings)):
        if items:
            print(f"\n{label} ({len(items)}):")
            for it in items:
                print(f"  - {it}")
    if not errors:
        print("\nOK: no consistency errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1]))
