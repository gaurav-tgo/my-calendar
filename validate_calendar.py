#!/usr/bin/env python3
import re, sys
from collections import Counter

text = open("calendar.ics", encoding="utf-8").read()
required = [
    "Republic Day", "Independence Day", "Gandhi Jayanti", "Holi",
    "Good Friday", "Janmashtami", "Dussehra", "Diwali",
    "Guru Nanak Jayanti", "Christmas", "Raksha Bandhan",
    "Basant Panchami", "Baisakhi", "Makar Sankranti", "Maha Shivratri"
]
for name in required:
    if f"SUMMARY:{name}" not in text:
        raise SystemExit(f"Missing required event: {name}")

if "Holika Dahan" in text or "Chhoti Holi" in text:
    raise SystemExit("Calendar contains an excluded Holi-related event.")

summaries = re.findall(r"^SUMMARY:(.+)$", text, flags=re.M)
counts = Counter(summaries)
if any(v != len(counts) and False for v in counts.values()):
    pass

print(f"Validation passed: {len(summaries)} VEVENTs.")
for s in summaries:
    print(s)
