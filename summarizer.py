"""
summarizer.py
-------------
Summarizes news articles using Groq API (free, fast).
"""

import json
import re
import time
import csv
from pathlib import Path
from groq import Groq

CLIENT = Groq(api_key="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")


def summarize_article(title, content, category):
    prompt = (
        f"You are a professional news editor. "
        f"Given the following {category} news headline and content, "
        f"write a clear and concise 3-sentence summary. "
        f"Be factual, neutral, and informative.\n\n"
        f"Headline: {title}\n\nContent: {content}\n\nSummary:"
    )
    try:
        response = CLIENT.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"    API error: {e}")
        return None


def score_fluency(text):
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 5]
    if not sentences:
        return 0.3
    avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
    if 10 <= avg_len <= 30:   return 1.0
    elif 5 <= avg_len < 10 or 30 < avg_len <= 40: return 0.75
    return 0.5

def score_relevance(title, summary):
    stop_words = {"the","a","an","is","are","was","were","be","been","have","has",
        "had","do","does","did","will","would","could","should","and",
        "or","but","in","on","at","to","for","of","with","by","it","this"}
    title_words   = set(title.lower().split()) - stop_words
    summary_words = set(summary.lower().split())
    if not title_words: return 0.5
    overlap = title_words & summary_words
    return round(min(len(overlap) / len(title_words) * 1.5, 1.0), 2)

def score_completeness(text):
    words = len(text.split())
    if 60 <= words <= 150:   return 1.0
    elif 40 <= words < 60:   return 0.75
    elif 150 < words <= 200: return 0.85
    elif words < 40:         return 0.4
    return 0.65

def score_conciseness(text):
    fillers = ["it is important to note","needless to say","in conclusion",
               "to summarize","in summary","that being said","first and foremost"]
    penalty = sum(0.08 for f in fillers if f in text.lower())
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 10]
    unique_ratio = len(set(s.lower() for s in sentences)) / max(len(sentences), 1)
    return round(max(min(unique_ratio - penalty, 1.0), 0.0), 2)

def score_diversity(summary, all_summaries):
    words = set(summary.lower().split())
    others = [set(s.lower().split()) for s in all_summaries if s != summary]
    if not others: return 1.0
    avg_overlap = sum(len(words & o) / max(len(words | o), 1) for o in others) / len(others)
    return round(min((1.0 - avg_overlap) * 1.5, 1.0), 2)

def overall_score(scores):
    weights = {"fluency": 0.20, "relevance": 0.30, "completeness": 0.25, "conciseness": 0.15, "diversity": 0.10}
    return round(sum(scores[d] * w for d, w in weights.items()), 2)

def score_summary(title, summary, all_summaries):
    scores = {
        "fluency":      score_fluency(summary),
        "relevance":    score_relevance(title, summary),
        "completeness": score_completeness(summary),
        "conciseness":  score_conciseness(summary),
        "diversity":    score_diversity(summary, all_summaries),
    }
    return scores, overall_score(scores)


def main():
    print("=" * 55)
    print("  NewsDigest — Summarizer & Dataset Builder")
    print("=" * 55 + "\n")

    with open("data/raw_news.json", encoding="utf-8") as f:
        articles = json.load(f)
    print(f"Loaded {len(articles)} articles.\n")

    summarized = []
    total = len(articles)
    print("Generating summaries...\n")

    for i, article in enumerate(articles):
        print(f"  [{i+1:>3}/{total}] {article['category']:<15} {article['title'][:50]}...")
        summary = summarize_article(article["title"], article["content"], article["category"])
        if summary:
            article["summary"] = summary
            summarized.append(article)
            print(f"         ✓ Done")
        else:
            print(f"         ✗ Skipped")
        time.sleep(1)

    print(f"\nSummarized {len(summarized)} articles.\n")

    with open("data/summarized_news.json", "w", encoding="utf-8") as f:
        json.dump(summarized, f, indent=2, ensure_ascii=False)
    print("Saved → data/summarized_news.json")

    print("\nScoring quality...\n")
    all_summaries = [a["summary"] for a in summarized]
    dataset = []

    for article in summarized:
        scores, final = score_summary(article["title"], article["summary"], all_summaries)
        dataset.append({
            "id": article["id"], "category": article["category"],
            "source": article["source"],
            "instruction": f"Summarize this news headline: {article['title']}",
            "headline": article["title"], "summary": article["summary"],
            "url": article["url"], "published_at": article["published_at"],
            "scores": scores, "overall_score": final,
            "quality_flag": "GOOD" if final >= 0.65 else "LOW",
        })
        flag = "✅" if final >= 0.65 else "⚠️"
        print(f"  {flag} [{article['id']}] Score: {final:.2f}  {article['title'][:45]}...")

    good = sum(1 for d in dataset if d["quality_flag"] == "GOOD")
    low  = sum(1 for d in dataset if d["quality_flag"] == "LOW")
    avg  = sum(d["overall_score"] for d in dataset) / len(dataset)

    print(f"\n── Quality Summary {'─'*35}")
    print(f"  Total    : {len(dataset)}\n  ✅ Good  : {good}\n  ⚠️  Low   : {low}\n  Avg score: {avg:.2f}")

    with open("data/dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print("\nSaved → data/dataset.json")

    with open("data/dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id","category","source","headline","summary","overall_score","quality_flag","url","published_at"])
        writer.writeheader()
        for d in dataset:
            writer.writerow({k: d[k] for k in ["id","category","source","headline","summary","overall_score","quality_flag","url","published_at"]})
    print("Saved → data/dataset.csv")

    with open("data/quality_report.txt", "w", encoding="utf-8") as f:
        f.write(f"NEWSDIGEST QUALITY REPORT\n{'='*55}\n\n")
        f.write(f"Total: {len(dataset)}  Good: {good}  Low: {low}  Avg: {avg:.2f}\n\n")
        f.write("PER CATEGORY\n" + "-"*40 + "\n")
        for cat in set(d["category"] for d in dataset):
            ci = [d for d in dataset if d["category"] == cat]
            f.write(f"{cat:<20} Avg: {sum(d['overall_score'] for d in ci)/len(ci):.2f}  Good: {sum(1 for d in ci if d['quality_flag']=='GOOD')}/{len(ci)}\n")
    print("Saved → data/quality_report.txt\n\nDone! Run: streamlit run app.py")


if __name__ == "__main__":
    main()