# Gaurav's Curated Dates

A deliberately small, read-only calendar feed containing only the dates selected in `config.json`.

## How it works

GitHub Actions generates `calendar.ics` from the selected event names in Drik Panchang's annual Indian calendar pages. Event matching is exact, so `Holi` cannot match `Holika Dahan` or `Chhoti Holi`.

The workflow refuses to publish an incomplete calendar and validates that there are exactly the configured event categories for each generated year.

## Current selections

Republic Day, Independence Day, Gandhi Jayanti, Holi, Good Friday, Janmashtami, Dussehra, Diwali, Guru Nanak Jayanti, Christmas, Raksha Bandhan, Basant Panchami, Baisakhi, Makar Sankranti, Maha Shivratri.

To change the calendar, edit `config.json` and run the workflow manually. Apple Calendar remains subscribed to the same feed URL.
