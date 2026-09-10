#!/usr/bin/env python3
import json, re, html
from datetime import date
from urllib.request import Request, urlopen

CONFIG_FILE = "config.json"
OUTPUT_FILE = "calendar.ics"

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

def fetch_year(year):
    url = f"https://www.drikpanchang.com/calendars/indian/indiancalendar.html?year={year}"
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as r:
        raw = r.read().decode("utf-8", errors="replace")

    # Convert the page to plain text. The calendar page presents events
    # in the form "Event Name Month Day, Year".
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    text = re.sub(r"\s+", " ", text)

    found = []
    for display_name, variants in config["events"].items():
        matches = []
        for variant in variants:
            pattern = rf"(?<![A-Za-z]){re.escape(variant)}\s+([A-Z][a-z]+)\s+(\d{{1,2}}),\s+{year}(?!\d)"
            for m in re.finditer(pattern, text, flags=re.I):
                month, day = m.group(1), int(m.group(2))
                matches.append((month, day))
        # Prefer the first matching date; duplicate variants can describe
        # the same festival.
        if matches:
            month, day = matches[0]
            from datetime import datetime
            dt = datetime.strptime(f"{month} {day} {year}", "%B %d %Y").date()
            found.append((dt, display_name))
        else:
            print(f"WARNING: could not find {display_name} for {year}")

    return found

events = []
current_year = date.today().year
# Keep two years available so the feed never becomes empty at year-end.
for year in (current_year, current_year + 1):
    events.extend(fetch_year(year))

events = sorted(set(events))

def esc(s):
    return (s.replace("\\", "\\\\")
             .replace(";", "\\;")
             .replace(",", "\\,")
             .replace("\n", "\\n"))

lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Gaurav-tgo//Curated Dates//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "X-WR-CALNAME:Gaurav's Dates",
    "X-WR-TIMEZONE:Asia/Kolkata",
    "X-PUBLISHED-TTL:P7D",
]

for dt, name in events:
    uid = f"{dt.isoformat()}-{re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')}@gaurav-tgo.github.io"
    next_day = dt.fromordinal(dt.toordinal() + 1)
    lines += [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{date.today().strftime('%Y%m%d')}T000000Z",
        f"DTSTART;VALUE=DATE:{dt.strftime('%Y%m%d')}",
        f"DTEND;VALUE=DATE:{next_day.strftime('%Y%m%d')}",
        f"SUMMARY:{esc(name)}",
        "TRANSP:TRANSPARENT",
        "END:VEVENT",
    ]

lines.append("END:VCALENDAR")

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\r\n") as f:
    f.write("\r\n".join(lines) + "\r\n")

print(f"Wrote {len(events)} events to {OUTPUT_FILE}")
