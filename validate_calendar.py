#!/usr/bin/env python3
"""Strict validation for the generated curated calendar."""
import json
import re
from collections import Counter
from pathlib import Path

cfg = json.loads(Path("config.json").read_text(encoding="utf-8"))
text = Path("calendar.ics").read_text(encoding="utf-8")

if not text.startswith("BEGIN:VCALENDAR") or not text.rstrip().endswith("END:VCALENDAR"):
    raise SystemExit("Invalid iCalendar envelope.")

summaries = re.findall(r"^SUMMARY:(.+)$", text, flags=re.M)
expected_names = list(cfg["events"])
expected_count = (int(cfg.get("years_ahead", 3)) + 1) * len(expected_names)

if len(summaries) != expected_count:
    raise SystemExit(f"Expected {expected_count} VEVENTs, found {len(summaries)}.")

allowed = set(expected_names)
unknown = sorted(set(summaries) - allowed)
if unknown:
    raise SystemExit("Unexpected events: " + ", ".join(unknown))

counts = Counter(summaries)
for name in expected_names:
    expected_per_year = int(cfg.get("years_ahead", 3)) + 1
    if counts[name] != expected_per_year:
        raise SystemExit(f"Expected {expected_per_year} occurrences of {name}, found {counts[name]}.")

# Explicit guard against the original Holi bug.
if "SUMMARY:Holika Dahan" in text or "SUMMARY:Chhoti Holi" in text:
    raise SystemExit("Excluded Holi-related event found.")

print(f"Validation passed: {len(summaries)} events; exactly {len(expected_names)} selected categories per year.")
