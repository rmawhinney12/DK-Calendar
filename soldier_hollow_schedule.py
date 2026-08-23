import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime


BASE_URL = "https://utaholympiclegacy.org/soho-events/"

headers = {
    "User-Agent": "Mozilla/5.0"
}


# ---------------------------------------------------------
# Months to download
# ---------------------------------------------------------

start_year = 2026
start_month = 8

end_year = 2027
end_month = 6


def month_range(start_year, start_month, end_year, end_month):

    year = start_year
    month = start_month

    while (year, month) <= (end_year, end_month):

        yield year, month

        month += 1

        if month > 12:
            month = 1
            year += 1


# ---------------------------------------------------------
# Download calendar pages
# ---------------------------------------------------------

all_events = []


for year, month in month_range(
    start_year,
    start_month,
    end_year,
    end_month
):

    month_string = f"{year}-{month:02d}"

    url = BASE_URL + f"?month={month_string}"

    print()
    print("=" * 60)
    print(f"DOWNLOADING {month_string}")
    print(url)

    response = requests.get(
        url,
        headers=headers
    )

    print("Status:", response.status_code)

    if response.status_code != 200:
        print("Skipping month")
        continue

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    # -----------------------------------------------------
    # Find event date elements
    # -----------------------------------------------------

    date_elements = soup.find_all(
        class_="event-date"
    )

    print(
        "Date elements found:",
        len(date_elements)
    )


    for date_element in date_elements:

        date_text = date_element.get_text(
            " ",
            strip=True
        )


        # -------------------------------------------------
        # Convert date to YYYY-MM-DD
        # -------------------------------------------------

        try:

            date_obj = datetime.strptime(
                f"{date_text}, {year}",
                "%A, %B %d, %Y"
            )

            formatted_date = date_obj.strftime(
                "%Y-%m-%d"
            )

        except ValueError:

            print(
                "Could not parse date:",
                date_text
            )

            continue


        # -------------------------------------------------
        # Find event container
        # -------------------------------------------------

        container = date_element

        for _ in range(5):

            if container.parent:
                container = container.parent

            text = container.get_text(
                "\n",
                strip=True
            )

            if len(text) > len(date_text) + 20:
                break


        # -------------------------------------------------
        # Extract text lines
        # -------------------------------------------------

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]


        # -------------------------------------------------
        # Remove the date from the beginning
        # -------------------------------------------------

        while lines and lines[0] == date_text:
            lines.pop(0)


        # -------------------------------------------------
        # Find event name
        # -------------------------------------------------

        event_name = ""

        if lines:
            event_name = lines[0]


        # -------------------------------------------------
        # Remaining text becomes description
        # -------------------------------------------------

        description_lines = []

        if len(lines) > 1:

            description_lines = lines[1:]


        description = " ".join(
            description_lines
        )


        # -------------------------------------------------
        # Clean up common website text
        # -------------------------------------------------

        description = description.replace(
            "Learn More and Register",
            ""
        ).strip()


        # -------------------------------------------------
        # Store event
        # -------------------------------------------------

        all_events.append({
            "Date": formatted_date,
            "Start Time": "",
            "End Time": "",
            "Event": event_name,
            "Description": description
        })


# ---------------------------------------------------------
# Remove duplicates
# ---------------------------------------------------------

unique_events = []

seen = set()


for event in all_events:

    key = (
        event["Date"],
        event["Event"],
        event["Description"]
    )

    if key not in seen:

        seen.add(key)

        unique_events.append(event)


all_events = unique_events


# ---------------------------------------------------------
# Sort chronologically
# ---------------------------------------------------------

all_events.sort(
    key=lambda event: (
        event["Date"],
        event["Start Time"]
    )
)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print()
print("=" * 60)
print("TOTAL EVENTS")
print("=" * 60)

print(
    "Events found:",
    len(all_events)
)


for event in all_events:

    print()
    print(
        event["Date"],
        "|",
        event["Event"]
    )

    if event["Description"]:
        print(
            event["Description"][:300]
        )


# ---------------------------------------------------------
# Save CSV
# ---------------------------------------------------------

output_file = "soldier_hollow_calendar.csv"


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
        "Description"
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(all_events)


print()
print("=" * 60)
print("SAVED")
print("=" * 60)

print(
    f"Saved {len(all_events)} events to:"
)

print(output_file)