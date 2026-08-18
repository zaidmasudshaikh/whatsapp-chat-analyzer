"""Parse exported WhatsApp chats into a dataframe used by the dashboard."""

from __future__ import annotations

import re

import pandas as pd


MESSAGE_PATTERN = re.compile(
    r"^\[?(?P<date>\d{1,2}[/-]\d{1,2}[/-]\d{2,4}),?\s+"
    r"(?P<time>\d{1,2}:\d{2}(?::\d{2})?(?:\s?[APap][Mm])?)\]?\s*-\s*"
    r"(?P<body>.*)$",
    re.MULTILINE,
)


def _parse_timestamp(date: str, time: str) -> pd.Timestamp:
    value = f"{date.replace('-', '/')} {time.upper().replace(' ', '')}"
    for day_first in (True, False):
        timestamp = pd.to_datetime(value, dayfirst=day_first, errors="coerce")
        if not pd.isna(timestamp):
            return timestamp
    return pd.NaT


def preprocess(data: str) -> pd.DataFrame:
    """Return messages and derived time columns from an exported chat string."""
    data = data.replace("\ufeff", "").replace("\r\n", "\n")
    matches = list(MESSAGE_PATTERN.finditer(data))
    if not matches:
        raise ValueError("No WhatsApp messages were found. Export the chat as a .txt file and try again.")

    records = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(data)
        body = (match.group("body") + data[match.end() : end]).rstrip("\n")
        sender, separator, message = body.partition(": ")
        user, message = (sender.strip(), message) if separator else ("group notification", body)
        records.append({"date": _parse_timestamp(match.group("date"), match.group("time")), "user": user, "message": message})

    df = pd.DataFrame(records).dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    if df.empty:
        raise ValueError("The chat timestamps could not be read. Please export the chat again.")

    df["only_date"] = df["date"].dt.date
    df["year"] = df["date"].dt.year
    df["month_num"] = df["date"].dt.month
    df["month"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["day_name"] = df["date"].dt.day_name()
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute
    df["period"] = df["hour"].map(lambda hour: f"{hour:02d}-{(hour + 1) % 24:02d}")
    return df
