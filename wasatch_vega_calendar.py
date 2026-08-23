import requests
import csv
from datetime import datetime
from zoneinfo import ZoneInfo


# --------------------------------------------------
# Vega organization information
# --------------------------------------------------

ORGANIZATION_ID = "XyGiUTtq1C1pBfthL9cQ"

API_URL = (
    f"https://api.vegaevents.com"
    f"/public/v2/events/organization/{ORGANIZATION_ID}/public"
)


# --------------------------------------------------
# Date range
# --------------------------------------------------

FROM_DATE = "2026-08-01T00:00:00Z"
TO_DATE = "2027-06-30T23:59:59Z"


# --------------------------------------------------
# Request settings
# --------------------------------------------------

headers = {
    "User-Agent": "Mozilla/5.0"
}

limit = 100
offset = 0

all_events = []


# --------------------------------------------------
# Download events
# --------------------------------------------------

while True:

    params = {
        "q": "*",
        "limit": limit,
        "offset": offset,
        "from": FROM_DATE,
        "to": TO_DATE
    }

    response = requests.get(
        API_URL,
        params=params,
        headers=headers
    )

    response.raise_for_status()

    data = response.json()

    events = data.get("items", [])

    print(
        f"Downloaded {len(events)} events "
        f"(offset {offset})"
    )

    all_events.extend(events)

    # If fewer than 100 came back,
    # we've reached the end.
    if len(events) < limit:
        break

    offset += limit


print()
print(f"Total events downloaded: {len(all_events)}")


# --------------------------------------------------
# Remove duplicate events
# --------------------------------------------------

seen = set()
unique_events = []

for event in all_events:

    event_id = event.get("id")

    if event_id not in seen:
        seen.add(event_id)
        unique_events.append(event)

all_events = unique_events

print(f"Unique events: {len(all_events)}")


# --------------------------------------------------
# Sort chronologically
# --------------------------------------------------

all_events.sort(
    key=lambda event: event.get("startTime", "")
)


# --------------------------------------------------
# Convert events into CSV rows
# --------------------------------------------------

rows = []

mountain = ZoneInfo("America/Denver")

for event in all_events:

    start = event.get("startTime")
    end = event.get("endTime")

    if not start:
        continue

    start_dt = datetime.fromisoformat(
        start.replace("Z", "+00:00")
    ).astimezone(mountain)

    end_dt = None

    if end:
        end_dt = datetime.fromisoformat(
            end.replace("Z", "+00:00")
        ).astimezone(mountain)

    # All-day events don't really need a start/end
    # time displayed.
    if event.get("isAllDay"):

        start_time = ""
        end_time = ""

    else:

        start_time = start_dt.strftime("%I:%M %p").lstrip("0")

        if end_dt:
            end_time = end_dt.strftime("%I:%M %p").lstrip("0")
        else:
            end_time = ""

    rows.append({
        "Date": start_dt.strftime("%Y-%m-%d"),
        "Start Time": start_time,
        "End Time": end_time,
        "Event": event.get("name", ""),
        "Description": event.get("description", ""),
        "Location": event.get("city", ""),
        "All Day": "Yes" if event.get("isAllDay") else "No"
    })


# --------------------------------------------------
# Write CSV
# --------------------------------------------------

output_file = "wasatch_vega_calendar.csv"

with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    fieldnames = [
        "Date",
        "Start Time",
        "End Time",
        "Event",
        "Description",
        "Location",
        "All Day"
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(rows)


print()
print(f"Saved {len(rows)} events to:")
print(output_file)