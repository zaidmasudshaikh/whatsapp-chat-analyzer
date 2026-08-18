# WhatsApp Chat Analyzer

A local Streamlit dashboard for exploring an exported WhatsApp chat. It reports message, word, media and link totals; timelines; activity patterns; active users; word frequencies; word clouds; and emoji usage.

## Requirements

- Python 3.10 or newer
- A WhatsApp chat export in `.txt` format

## Run locally

```bash
git clone <your-repository-url>
cd whatsapp-chat-analyzer-master
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the URL Streamlit prints, normally `http://localhost:8501`.

## Export a chat

In WhatsApp, open a chat, then choose **Export chat** and select **Without media**. Upload the resulting `.txt` file from the sidebar. The app supports common Android (12/24-hour) and bracketed iOS-style timestamps. It does not upload the content anywhere itself; processing happens in the running Streamlit session.

## Troubleshooting

- **“No WhatsApp messages were found”**: upload the exported `.txt` file, not a screenshot or copied conversation.
- **Strange characters**: export the chat again; the app reads UTF-8 and safely replaces invalid byte sequences.
- **Empty charts or word cloud**: the selected user may only have media, system notices, or stop words.

## Project layout

- `app.py` — Streamlit UI and visualizations
- `preprocessor.py` — WhatsApp export parser
- `helper.py` — analysis functions
- `stop_hinglish.txt` — stop-word list for text analysis
- `tests/test_analysis.py` — parser and analysis regression tests

## Test

```bash
python -m unittest discover -s tests -v
```
