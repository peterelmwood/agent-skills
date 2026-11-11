# Contract: `scripts/check_plan.py` command line

```text
python check_plan.py <path-to-steps.md>
```

| Situation | stdout | Exit |
|---|---|---|
| Wrong number of arguments | Module docstring (usage) | 2 |
| File has no recognisable steps | `ERROR: no steps found …` | 1 |
| Errors found | Summary, available now, waiting-on gates, `ERRORS (n):` list, optional `WARNINGS (n):` | 1 |
| No errors | Summary, available now, waiting-on gates, optional warnings, `OK: no consistency errors.` | 0 |

Summary line: `Steps: <n> · Gates: <g> · Done: <d> · Active effort: ~<h> h`.

**Errors**: duplicate ID; missing `Needs:`; unreadable `Needs` entry; unknown `Needs` ID;
missing `Done when`; parent without children; parent ticked before all children; dependency
cycle; parallel line with unknown ID; parallel line where one ID depends on another; no
available step while work remains.

**Warnings**: children without a parent marker; all children ticked but parent not; missing
estimate; over 30 minutes without `exception`; ticked while a `Needs` is unticked.

**Encoding**: input read as UTF-8; stdout reconfigured to UTF-8, so emoji output never
raises `UnicodeEncodeError` on a cp1252 console.

**Dependencies**: Python 3.8+ standard library only.
