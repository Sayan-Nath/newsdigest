"""
fetch_news.py
-------------
Fetches live news headlines from NewsAPI across multiple categories.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

NEWS_API_KEY = "api_token"
BASE_URL     = "https://newsapi.org/v2/top-headlines"

CATEGORIES = ["technology", "sports", "business", "science", "health", "entertainment"]

COUNTRY = "us"


def fetch_category(category, page_size=10):
    """Fetch top headlines for a given category."""
    params = {
        "apiKey":   NEWS_API_KEY,
        "category": category,
        "country":  COUNTRY,
        "pageSize": page_size,
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        articles = []
        for i, article in enumerate(data.get("articles", [])):
            if not article.get("title") or not article.get("description"):
                continue
            if article["title"] == "[Removed]":
                continue
            articles.append({
                "id":          f"{category}_{i+1}",
                "category":    category.capitalize(),
                "title":       article["title"],
                "description": article.get("description", ""),
                "content":     article.get("content", article.get("description", "")),
                "source":      article.get("source", {}).get("name", "Unknown"),
                "url":         article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "fetched_at":  datetime.now().isoformat(),
            })
        return articles
    except Exception as e:
        print(f"  Error fetching {category}: {e}")
        return []


def fetch_all(categories=CATEGORIES, page_size=10):
    """Fetch news from all categories."""
    all_articles = []
    print("Fetching live news...\n")
    for category in categories:
        print(f"  Fetching {category.capitalize()}...")
        articles = fetch_category(category, page_size)
        all_articles.extend(articles)
        print(f"  Got {len(articles)} articles")
    print(f"\nTotal: {len(all_articles)} articles fetched.")
    return all_articles


def save_raw(articles, path="data/raw_news.json"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"Saved → {path}")


if __name__ == "__main__":
    articles = fetch_all()
    save_raw(articles)
