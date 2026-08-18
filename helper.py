"""Analysis helpers for the WhatsApp chat dashboard."""

from collections import Counter
from pathlib import Path
import re

import emoji
import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud

extract = URLExtract()
MEDIA_MARKERS = {"<media omitted>", "<attached: ", "image omitted", "video omitted"}
STOP_WORDS = set(Path(__file__).with_name("stop_hinglish.txt").read_text(encoding="utf-8").split())


def _filtered(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    return df if selected_user == "Overall" else df[df["user"] == selected_user]


def _is_media(message: str) -> bool:
    lowered = message.strip().lower()
    return any(lowered == marker or lowered.startswith(marker) for marker in MEDIA_MARKERS)


def _messages_for_words(selected_user: str, df: pd.DataFrame) -> pd.Series:
    data = _filtered(selected_user, df)
    return data.loc[(data["user"] != "group notification") & ~data["message"].map(_is_media), "message"]


def _words(messages: pd.Series) -> list[str]:
    return [word for message in messages for word in re.findall(r"\b[^\W_]+\b", message.lower()) if word not in STOP_WORDS]


def fetch_stats(selected_user, df):
    data = _filtered(selected_user, df)
    messages = data["message"].fillna("")
    links = sum((extract.find_urls(message) for message in messages), [])
    return len(data), sum(len(message.split()) for message in messages), sum(messages.map(_is_media)), len(links)


def most_busy_user(df):
    people = df[df["user"] != "group notification"]["user"]
    counts = people.value_counts().head()
    total = len(people)
    percentages = people.value_counts().div(total).mul(100).round(2) if total else pd.Series(dtype=float)
    return counts, percentages.rename_axis("Name").reset_index(name="Percent")


def create_cloud(selected_user, df):
    text = " ".join(_words(_messages_for_words(selected_user, df)))
    return WordCloud(width=700, height=450, min_font_size=10, max_font_size=100, background_color="white").generate(text) if text else None


def most_common_words(selected_user, df):
    return pd.DataFrame(Counter(_words(_messages_for_words(selected_user, df))).most_common(25), columns=["Word", "Count"])


def emoji_helper(selected_user, df):
    messages = _filtered(selected_user, df)["message"].fillna("")
    found = [character for message in messages for character in message if character in emoji.EMOJI_DATA]
    return pd.DataFrame(Counter(found).most_common(), columns=["Emoji", "Count"])


def monthly_timeline(selected_user, df):
    data = _filtered(selected_user, df)
    return data.groupby(["year", "month_num", "month"], as_index=False).size().rename(columns={"size": "message"}).assign(time=lambda item: item["month"].str[:3] + " " + item["year"].astype(str))


def daily_timeline(selected_user, df):
    return _filtered(selected_user, df).groupby("only_date", as_index=False).size().rename(columns={"size": "message"})


def weekly_activity_map(selected_user, df):
    return _filtered(selected_user, df)["day_name"].value_counts().reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], fill_value=0)


def monthly_activity_map(selected_user, df):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return _filtered(selected_user, df)["month"].value_counts().reindex(months, fill_value=0)


def activity_heatmap(selected_user, df):
    data = _filtered(selected_user, df)
    columns = [f"{hour:02d}-{(hour + 1) % 24:02d}" for hour in range(24)]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return data.pivot_table(index="day_name", columns="period", values="message", aggfunc="count", fill_value=0).reindex(index=days, columns=columns, fill_value=0)
