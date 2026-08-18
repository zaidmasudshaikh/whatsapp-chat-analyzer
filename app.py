"""Streamlit entry point for the WhatsApp Chat Analyzer."""

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

import helper
import preprocessor


st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon="💬", layout="wide")
st.title("💬 WhatsApp Chat Analyzer")
st.caption("Upload a WhatsApp .txt export. Your chat is processed only in this app session.")


def show_plot(title, data, x, y, kind="line", rotation=45):
    if data.empty:
        st.info(f"No data is available for {title.lower()}.")
        return
    figure, axis = plt.subplots(figsize=(10, 4))
    if kind == "bar":
        axis.bar(data.index if x is None else data[x], data.values if y is None else data[y])
    else:
        axis.plot(data[x], data[y], color="#25D366", marker="o", markersize=3)
    axis.tick_params(axis="x", rotation=rotation)
    axis.set_title(title)
    figure.tight_layout()
    st.pyplot(figure, clear_figure=True)


uploaded_file = st.sidebar.file_uploader("Choose an exported WhatsApp chat", type=["txt"])
if uploaded_file is None:
    st.info("Export a chat from WhatsApp (preferably **Without media**) and upload its .txt file to begin.")
    st.stop()

try:
    raw = uploaded_file.getvalue().decode("utf-8-sig")
except UnicodeDecodeError:
    raw = uploaded_file.getvalue().decode("utf-8", errors="replace")

try:
    df = preprocessor.preprocess(raw)
except ValueError as error:
    st.error(str(error))
    st.stop()

users = sorted(user for user in df["user"].dropna().unique() if user != "group notification")
selected_user = st.sidebar.selectbox("Show analysis for", ["Overall", *users])

if not st.sidebar.button("Show analysis", type="primary"):
    st.stop()

num_messages, words, media_messages, links = helper.fetch_stats(selected_user, df)
st.subheader("Top statistics")
for column, label, value in zip(st.columns(4), ["Messages", "Words", "Media shared", "Links shared"], [num_messages, words, media_messages, links]):
    column.metric(label, value)

st.subheader("Message timelines")
left, right = st.columns(2)
with left:
    show_plot("Monthly timeline", helper.monthly_timeline(selected_user, df), "time", "message")
with right:
    show_plot("Daily timeline", helper.daily_timeline(selected_user, df), "only_date", "message")

st.subheader("Activity")
left, right = st.columns(2)
with left:
    busy_day = helper.weekly_activity_map(selected_user, df)
    show_plot("Most active day", busy_day, None, None, kind="bar")
with right:
    busy_month = helper.monthly_activity_map(selected_user, df)
    show_plot("Most active month", busy_month, None, None, kind="bar")

heatmap = helper.activity_heatmap(selected_user, df)
figure, axis = plt.subplots(figsize=(14, 4))
sns.heatmap(heatmap, ax=axis, cmap="YlGnBu")
axis.set_title("Weekly activity map")
figure.tight_layout()
st.pyplot(figure, clear_figure=True)

if selected_user == "Overall":
    counts, percentages = helper.most_busy_user(df)
    st.subheader("Most active users")
    left, right = st.columns(2)
    with left:
        show_plot("Messages by user", counts, None, None, kind="bar")
    with right:
        st.dataframe(percentages, hide_index=True, use_container_width=True)

st.subheader("Word cloud")
cloud = helper.create_cloud(selected_user, df)
if cloud is None:
    st.info("There are no non-stop-word text messages available for a word cloud.")
else:
    figure, axis = plt.subplots(figsize=(8, 5))
    axis.imshow(cloud, interpolation="bilinear")
    axis.axis("off")
    st.pyplot(figure, clear_figure=True)

st.subheader("Most common words")
common_words = helper.most_common_words(selected_user, df)
if common_words.empty:
    st.info("No common words to display.")
else:
    figure, axis = plt.subplots(figsize=(9, 6))
    axis.barh(common_words["Word"], common_words["Count"], color="#128C7E")
    axis.invert_yaxis()
    figure.tight_layout()
    st.pyplot(figure, clear_figure=True)

st.subheader("Emoji analysis")
emoji_df = helper.emoji_helper(selected_user, df)
if emoji_df.empty:
    st.info("No emoji were found in this selection.")
else:
    left, right = st.columns(2)
    with left:
        st.dataframe(emoji_df, hide_index=True, use_container_width=True)
    with right:
        figure, axis = plt.subplots()
        top = emoji_df.head(10)
        axis.pie(top["Count"], labels=top["Emoji"], autopct="%1.1f%%")
        st.pyplot(figure, clear_figure=True)
