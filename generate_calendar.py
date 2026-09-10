#!/usr/bin/env python3
import json
import re
import urllib.request
from datetime import date, timedelta

MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

def fetch_text(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (calendar generator; +https://github.com/Gaurav-tgo/my-calendar)"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode("utf-8", errors="replace")
    # Remove tags without adding misleading word boundaries.
    raw = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"&nbsp;|&#160;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"\s+", " ", text)
    return text

def find_event(text, aliases, year):
    # Exact event-name matching is important: "Holi" must NOT match "Holika Dahan".
    for alias in aliases:
        pattern = re.compile(
            rf"(?<!\w){re.escape(alias)}(?!\w)\s+"
            rf"(January|February|March|April|May|June|July|August|September|October|November|December)"
            rf"\s+(\d{{1,2}}),\s+{year}\b",
            re.I
        )
        m = pattern.search(text)
        if m:
            month = MONTHS[m.group(1).title()]
            day = int(m.group(2))
            return date(year, month, day), alias
    return None, None

def esc(s):
    return (s.replace("\\", "\\\\").replace(";", "\\;")
             .replace(",", "\\,").replace("\n", "\\n"))

def make_uid(name, d):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{d:%Y%m%d}-{slug}@gaurav-tgo.github.io"

def main():
    with open("config.json", encoding="utf-8") as f:
        cfg = json.load(f)

    today = date.today()
    years = range(today.year, today.year + int(cfg.get("years_ahead", 3)) + 1)
    found = []
    missing = []

    for year in years:
        url = cfg["source"].format(year=year)
        text = fetch_text(url)
        for name, aliases in cfg["events"].items():
            d, matched = find_event(text, aliases, year)
            if d is None:
                missing.append(f"{year}: {name}")
            else:
                found.append((d, name, matched, url))

    if missing:
        raise SystemExit(
            "Refusing to publish an incomplete calendar. Missing:\n  " +
            "\n  ".join(missing)
        )

    found.sort(key=lambda x: (x[0], x[1]))
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Gaurav-tgo//Curated Dates//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:" + esc(cfg["calendar_name"]),
        "X-WR-TIMEZONE:" + cfg.get("timezone", "Asia/Kolkata"),
        "X-PUBLISHED-TTL:P30D",
    ]

    for d, name, matched, source in found:
        lines += [
            "BEGIN:VEVENT",
            "UID:" + make_uid(name, d),
            f"DTSTAMP:{datetime.datetime.utcnow():%Y%m%dT%H%M%SZ}",
            f"DTSTART;VALUE=DATE:{d:%Y%m%d}",
            f"DTEND;VALUE=DATE:{(d + timedelta(days=1)):%Y%m%d}",
            "SUMMARY:" + esc(name),
            "DESCRIPTION:" + esc(f"Curated date. Source: Drik Panchang. Matched as: {matched}."),
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    with open("calendar.ics", "w", encoding="utf-8", newline="\r\n") as f:
        f.write("\r\n".join(lines) + "\r\n")

    print(f"Generated {len(found)} events across {len(list(years))} years.")

if __name__ == "__main__":
    main()
