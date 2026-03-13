# NewsDigest 📰

An AI-powered news reader that fetches live headlines and generates clean summaries using Claude. Browse news by category, search across topics, and read concise AI-generated summaries — all in one place.

## What it does

- Fetches live news from 6 categories using NewsAPI
- Generates clean 3-sentence summaries using Claude AI
- Scores each summary on quality (fluency, relevance, completeness)
- Streamlit UI with category browsing, search, and export

## Categories

Technology 💻 | Sports ⚽ | Business 📈 | Science 🔬 | Health 🏥 | Entertainment 🎬

## Project Structure

```
NewsDigest/
├── data/
│   ├── raw_news.json            # Fetched headlines
│   ├── summarized_news.json     # Articles with summaries
│   ├── dataset.json             # Full dataset with scores
│   ├── dataset.csv              # CSV format
│   └── quality_report.txt       # Quality breakdown
├── fetch_news.py                # Fetches live news from NewsAPI
├── summarizer.py                # Generates summaries + scores quality
├── app.py                       # Streamlit news reader UI
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

Set API keys:
```bash
# Windows
set ANTHROPIC_API_KEY=your_anthropic_key
set NEWS_API_KEY=your_newsapi_key

# Mac/Linux
export ANTHROPIC_API_KEY=your_anthropic_key
export NEWS_API_KEY=your_newsapi_key
```

## Usage

### Step 1 — Fetch live news
```bash
python fetch_news.py
```

### Step 2 — Generate summaries
```bash
python summarizer.py
```

### Step 3 — Launch the app
```bash
streamlit run app.py
```
