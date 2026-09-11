#!/usr/bin/env python3
"""Generate the curated calendar from Drik Panchang's annual Indian calendar pages.

Important design choice: event names are matched exactly, including word boundaries.
This prevents e.g. Holi from matching Holika Dahan or Chhoti Holi.
"""
import datetime as dt
import html
import json
import re
import urllib.request
from pathlib import Path

MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}
MONTH_RE = "|".join(MONTHS)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; GauravCuratedCalendar/2.0; +https://github.com/Gaurav-tgo/my-calendar)"
        },
    )
    with urllib.request.urlopen(req, timeout=45) as response:
        raw = response.read().decode("utf-8", errors="replace")
    raw = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def find_event(text: str, aliases: list[str], year: int):
    """Return the date for the first exact alias occurrence in the requested year."""
    for alias in aliases:
        pattern = re.compile(
            rf"(?<![\w]){re.escape(alias)}(?![\w])\s+"
            rf"({MONTH_RE})\s+(\d{{1,2}}),\s+{year}(?!\d)",
            flags=re.I,
        )
        match = pattern.search(text)
        if not match:
            continue
        month = MONTHS[match.group(1).title()]
        day = int(match.group(2))
        return dt.date(year, month, day), alias
    return None, None


def esc(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def uid(name: str, event_date: dt.date) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{event_date:%Y%m%d}-{slug}@gaurav-tgo.github.io"


def main():
    cfg = json.loads(Path("config.json").read_text(encoding="utf-8"))
    today = dt.date.today()
    years = list(range(today.year, today.year + int(cfg.get("years_ahead", 3)) + 1))

    events = []
    missing = []
    for year in years:
        source_url = cfg["source"].format(year=year)
        text = fetch_text(source_url)
        for name, aliases in cfg["events"].items():
            event_date, matched = find_event(text, aliases, year)
            if event_date is None:
                missing.append(f"{year}: {name}")
            else:
                events.append((event_date, name, matched, source_url))

    if missing:
        raise SystemExit(
            "Refusing to publish an incomplete calendar. Missing:\n  "
            + "\n  ".join(missing)
        )

    # One and only one occurrence of each configured event per year.
    expected = len(years) * len(cfg["events"])
    if len(events) != expected:
        raise SystemExit(f"Expected {expected} events, found {len(events)}.")

    seen = set()
    for event_date, name, _, _ in events:
        key = (event_date.year, name)
        if key in seen:
            raise SystemExit(f"Duplicate event: {event_date.year}: {name}")
        seen.add(key)

    events.sort(key=lambda item: (item[0], item[1]))
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
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

    for event_date, name, matched, source_url in events:
        lines.extend([
            "BEGIN:VEVENT",
            "UID:" + uid(name, event_date),
            "DTSTAMP:" + now,
            f"DTSTART;VALUE=DATE:{event_date:%Y%m%d}",
            f"DTEND;VALUE=DATE:{(event_date + dt.timedelta(days=1)):%Y%m%d}",
            "SUMMARY:" + esc(name),
            "DESCRIPTION:" + esc(f"Curated date. Source: Drik Panchang. Exact match: {matched}."),
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ])

    lines.append("END:VCALENDAR")
    Path("calendar.ics").write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    print(f"Generated {len(events)} events across {len(years)} years.")


if __name__ == "__main__":
    main()
