import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time
import csv


# -----------------------------
# Settings
# -----------------------------

API_URL = "https://hebervalleyrr.antix.io/api/product/frontinstances"

TIMEZONE = ZoneInfo("America/Denver")

start = int(time.time())
end = start + (365 * 24 * 60 * 60)


# -----------------------------
# Get data
# -----------------------------

url = f"{API_URL}?start={start}&end={end}"

print("Downloading schedule...")

response = requests.get(url)
response.raise_for_status()

data = response.json()

print(f"Found {len(data)} train types")


# -----------------------------
# Process events
# -----------------------------

events = []

now = datetime.now(TIMEZONE)


for train in data:

    train_name = train.get("name", "Unknown Train")

    for instance in train.get("instances", []):

        start_timestamp = instance["startDate"] / 1000
        end_timestamp = instance["endDate"] / 1000

        start_time = datetime.fromtimestamp(
            start_timestamp,
            TIMEZONE
        )

        end_time = datetime.fromtimestamp(
            end_timestamp,
            TIMEZONE
        )

        # Skip past events
        if start_time < now:
            continue

        duration = end_time - start_time

        events.append({
            "train": train_name,
            "start": start_time,
            "end": end_time,
            "duration": int(duration.total_seconds() / 60)
        })


# -----------------------------
# Sort events
# -----------------------------

events.sort(key=lambda x: x["start"])


# -----------------------------
# Display
# -----------------------------

print("\n==============================")
print("HEBER VALLEY RAILROAD SCHEDULE")
print("==============================\n")


for event in events:

    print(
        f"🚂 {event['train']}\n"
        f"   {event['start'].strftime('%A, %B %d, %Y')}\n"
        f"   {event['start'].strftime('%I:%M %p')} - "
        f"{event['end'].strftime('%I:%M %p')}\n"
        f"   Duration: {event['duration']} minutes\n"
    )


print(f"Total departures: {len(events)}")


# -----------------------------
# Export CSV
# -----------------------------

with open("heber_schedule.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Train",
        "Date",
        "Start Time",
        "End Time",
        "Duration (Minutes)"
    ])

    for event in events:

        writer.writerow([
            event["train"],
            event["start"].strftime("%Y-%m-%d"),
            event["start"].strftime("%I:%M %p"),
            event["end"].strftime("%I:%M %p"),
            event["duration"]
        ])


print("\nSaved: heber_schedule.csv")
