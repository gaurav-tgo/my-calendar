# Gaurav's Curated Dates

A deliberately small, read-only calendar feed for dates worth being aware of.

## Included

- Republic Day
- Independence Day
- Gandhi Jayanti
- Holi
- Good Friday
- Janmashtami
- Dussehra
- Diwali
- Guru Nanak Jayanti
- Christmas
- Raksha Bandhan
- Basant Panchami
- Baisakhi
- Makar Sankranti
- Maha Shivratri

## Source and safety checks

The generator reads the annual Indian calendar from Drik Panchang and uses **exact event-name matching**. In particular, `Holi` cannot match `Holika Dahan`.

The workflow refuses to publish if any selected event is missing, then validates that excluded Holi-related events have not slipped into the feed.

GitHub Actions regenerates the feed monthly and can also be run manually.

The resulting `calendar.ics` is intended to be published through GitHub Pages and subscribed to from Apple Calendar.
