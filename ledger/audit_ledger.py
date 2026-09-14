"""Count the claim ledger FROM THE FILE, because three typed totals were wrong.

    python audit_ledger.py CLAIM_LEDGER.md

WHAT THIS COUNTS, AND WHAT IT CANNOT
    It counts the one table above "# REVISION 1", which since 2026-09-10 carries
    CURRENT verdicts: the three revisions were folded in and are kept below it as
    dated history, marked superseded. Before that fold the ledger held state as a
    baseline plus three prose delta tables, so current state existed nowhere, and
    all three published totals were typed and all three were wrong.

    Run this before quoting any total. Do not type one.
"""
import io, re, sys, collections
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

p = sys.argv[1]
s = io.open(p, encoding="utf-8").read()
if "LEDGER:BEGIN" not in s or "LEDGER:END" not in s:
    sys.exit("CLAIM_LEDGER.md has no LEDGER:BEGIN/LEDGER:END markers. Refusing "
             "to guess which table is authoritative -- guessing is how three "
             "published totals came to be wrong.")
base = s.split("LEDGER:BEGIN", 1)[1].split("LEDGER:END", 1)[0]

VERDICTS = ("SUPPORTED", "PARTIAL", "PENDING-MACHINE", "PENDING-AUTHOR",
            "UNSUPPORTED")
rows = []
for line in base.splitlines():
    m = re.match(r"^\|\s*\*\*([A-Z][-A-Za-z0-9]*)\*\*\s*\|(.*)\|\s*$", line)
    if not m:
        continue
    rid, rest = m.group(1), m.group(2)
    last = rest.rsplit("|", 1)[-1]
    hit = [v for v in VERDICTS if v in last]
    # PENDING-MACHINE contains no substring clash; UNSUPPORTED does not contain
    # SUPPORTED as a separate token but DOES as a substring -- disambiguate.
    if "UNSUPPORTED" in last:
        hit = ["UNSUPPORTED"]
    elif "PENDING-MACHINE" in last:
        hit = ["PENDING-MACHINE"]
    elif "PENDING-AUTHOR" in last:
        hit = ["PENDING-AUTHOR"]
    elif "PARTIAL" in last:
        hit = ["PARTIAL"]
    elif "SUPPORTED" in last:
        hit = ["SUPPORTED"]
    rows.append((rid, hit[0] if hit else "??? " + last.strip()[:60]))

print("CURRENT state: revisions were folded into the table 2026-09-10;")
print("the REVISION sections below it are history and are not counted.")
print("rows parsed:", len(rows))
c = collections.Counter(v for _, v in rows)
for k in sorted(c):
    print("  %-16s %d" % (k, c[k]))
print("  %-16s %d" % ("TOTAL", sum(c.values())))
print()
dup = [k for k, n in collections.Counter(r for r, _ in rows).items() if n > 1]
print("duplicate ids:", dup or "none")
print()
for rid, v in rows:
    print("  %-6s %s" % (rid, v))
