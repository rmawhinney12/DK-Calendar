import csv
from datetime import datetime


# ---------------------------------------------------------
# Files
# ---------------------------------------------------------

FILES = {
    "Wasatch Vega": "wasatch_vega_calendar.csv",
    "Deer Creek Vega": "deer_creek_vega_calendar.csv",
    "Heber Valley Railroad": "heber_schedule.csv",
    "Soldier Hollow": "soldier_hollow_calendar.csv",
}


rows = []


# ---------------------------------------------------------
# Wasatch Vega
# ---------------------------------------------------------

with open(
    FILES["Wasatch Vega"],
    "r",
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        rows.append({
            "Date": row["Date"],
            "Start Time": row["Start Time"],
            "End Time": row["End Time"],
            "Event": row["Event"],
            "Description": row["Description"],
            "Source": "Wasatch HS",
        })


# ---------------------------------------------------------
# Deer Creek Vega
# ---------------------------------------------------------

with open(
    FILES["Deer Creek Vega"],
    "r",
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        rows.append({
            "Date": row["Date"],
            "Start Time": row["Start Time"],
            "End Time": row["End Time"],
            "Event": row["Event"],
            "Description": row["Description"],
            "Source": "Deer Creek HS",
        })


# ---------------------------------------------------------
# Heber Valley Railroad
# ---------------------------------------------------------

with open(
    FILES["Heber Valley Railroad"],
    "r",
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        rows.append({
            "Date": row["Date"],
            "Start Time": row["Start Time"],
            "End Time": row["End Time"],
            "Event": row["Train"],
            "Description": "",
            "Source": "Heber Valley Railroad",
        })


# ---------------------------------------------------------
# Soldier Hollow
# ---------------------------------------------------------

with open(
    FILES["Soldier Hollow"],
    "r",
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        rows.append({
            "Date": row["Date"],
            "Start Time": row["Start Time"],
            "End Time": row["End Time"],
            "Event": row["Event"],
            "Description": row["Description"],
            "Source": "Soldier Hollow",
        })


# ---------------------------------------------------------
# Sort by date and start time
# ---------------------------------------------------------

rows.sort(
    key=lambda x: (
        x["Date"],
        x["Start Time"]
    )
)


# =========================================================
# SAVE COMBINED CSV
# =========================================================

csv_output = "combined_calendar.csv"

fieldnames = [
    "Date",
    "Start Time",
    "End Time",
    "Source",
    "Event",
    "Description",
]


with open(
    csv_output,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(rows)


print()
print(f"Saved CSV: {csv_output}")


# =========================================================
# CREATE ICS CALENDAR
# =========================================================

ics_output = "combined_calendar.ics"


def escape_ics_text(text):
    """
    Escape characters that have special meaning in ICS files.
    """

    if not text:
        return ""

    text = str(text)

    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "")

    return text


def format_ics_datetime(date_string, time_string):
    """
    Convert:
        2026-08-13
        6:30 PM

    into:
        20260813T183000

    We use America/Denver for the calendar.
    """

    if not time_string:
        return None

    dt = datetime.strptime(
        f"{date_string} {time_string}",
        "%Y-%m-%d %I:%M %p"
    )

    return dt.strftime("%Y%m%dT%H%M%S")


with open(
    ics_output,
    "w",
    encoding="utf-8",
    newline=""
) as f:

    # Calendar header

    f.write("BEGIN:VCALENDAR\r\n")
    f.write("VERSION:2.0\r\n")
    f.write("PRODID:-//DK Calendar//Combined Calendar//EN\r\n")
    f.write("CALSCALE:GREGORIAN\r\n")
    f.write("METHOD:PUBLISH\r\n")
    f.write("X-WR-CALNAME:DK Combined Calendar\r\n")
    f.write("X-WR-TIMEZONE:America/Denver\r\n")

    # -----------------------------------------------------
    # Events
    # -----------------------------------------------------

    for index, row in enumerate(rows):

        date_string = row["Date"]
        start_time = row["Start Time"]
        end_time = row["End Time"]

        event_name = row["Event"]
        source = row["Source"]
        description = row["Description"]

        # -------------------------------------------------
        # Create a unique ID for each event
        # -------------------------------------------------

        uid = (
            f"{date_string}-"
            f"{index}-"
            f"dkcalendar@combined"
        )

        # -------------------------------------------------
        # All-day event
        # -------------------------------------------------

        if not start_time:

            # ICS all-day events use the following day
            # as the exclusive end date.

            event_date = datetime.strptime(
                date_string,
                "%Y-%m-%d"
            )

            from datetime import timedelta

            next_day = event_date + timedelta(days=1)

            start_value = event_date.strftime("%Y%m%d")
            end_value = next_day.strftime("%Y%m%d")

            f.write("BEGIN:VEVENT\r\n")
            f.write(f"UID:{uid}\r\n")
            f.write(f"DTSTART;VALUE=DATE:{start_value}\r\n")
            f.write(f"DTEND;VALUE=DATE:{end_value}\r\n")

        # -------------------------------------------------
        # Timed event
        # -------------------------------------------------

        else:

            start_value = format_ics_datetime(
                date_string,
                start_time
            )

            if end_time:

                end_value = format_ics_datetime(
                    date_string,
                    end_time
                )

            else:

                # If no end time exists,
                # default to one hour.

                start_dt = datetime.strptime(
                    f"{date_string} {start_time}",
                    "%Y-%m-%d %I:%M %p"
                )

                from datetime import timedelta

                end_dt = start_dt + timedelta(hours=1)

                end_value = end_dt.strftime(
                    "%Y%m%dT%H%M%S"
                )

            f.write("BEGIN:VEVENT\r\n")
            f.write(f"UID:{uid}\r\n")
            f.write(
                f"DTSTART;TZID=America/Denver:"
                f"{start_value}\r\n"
            )
            f.write(
                f"DTEND;TZID=America/Denver:"
                f"{end_value}\r\n"
            )

        # -------------------------------------------------
        # Event title
        # -------------------------------------------------

        title = f"{source} — {event_name}"

        f.write(
            f"SUMMARY:{escape_ics_text(title)}\r\n"
        )

        # -------------------------------------------------
        # Description
        # -------------------------------------------------

        if description:

            f.write(
                f"DESCRIPTION:"
                f"{escape_ics_text(description)}\r\n"
            )

        # -------------------------------------------------
        # End event
        # -------------------------------------------------

        f.write("END:VEVENT\r\n")

    # Calendar footer

    f.write("END:VCALENDAR\r\n")


print(f"Saved ICS: {ics_output}")


# =========================================================
# SUMMARY
# =========================================================

print()
print("=" * 60)
print("COMBINED CALENDAR")
print("=" * 60)

print(
    f"Wasatch HS:                "
    f"{sum(1 for r in rows if r['Source'] == 'Wasatch HS')}"
)

print(
    f"Deer Creek HS:             "
    f"{sum(1 for r in rows if r['Source'] == 'Deer Creek HS')}"
)

print(
    f"Heber Valley Railroad:     "
    f"{sum(1 for r in rows if r['Source'] == 'Heber Valley Railroad')}"
)

print(
    f"Soldier Hollow:            "
    f"{sum(1 for r in rows if r['Source'] == 'Soldier Hollow')}"
)

print("-" * 60)

print(
    f"TOTAL EVENTS:              "
    f"{len(rows)}"
)

print()
print(f"CSV: {csv_output}")
print(f"ICS: {ics_output}")