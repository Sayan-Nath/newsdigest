"""
app.py
------
NewsDigest — AI-powered news reader with summarization.
Browse live news by category, read AI summaries, and export dataset.
"""

import json
import webbrowser
from pathlib import Path
from collections import Counter
import streamlit as st

DATA_PATH = Path("data/dataset.json")
RAW_PATH  = Path("data/summarized_news.json")

CATEGORY_COLORS = {
    "Technology":    "#4ECDC4",
    "Sports":        "#FF6B6B",
    "Business":      "#FFD93D",
    "Science":       "#A8E6CF",
    "Health":        "#C3B1E1",
    "Entertainment": "#FFB347",
}

CATEGORY_ICONS = {
    "Technology":    "💻",
    "Sports":        "⚽",
    "Business":      "📈",
    "Science":       "🔬",
    "Health":        "🏥",
    "Entertainment": "🎬",
}


@st.cache_data
def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def news_card(item):
    color = CATEGORY_COLORS.get(item["category"], "#DDD")
    icon  = CATEGORY_ICONS.get(item["category"], "📰")
    flag  = "✅" if item["quality_flag"] == "GOOD" else "⚠️"

    st.markdown(
        f'<div style="background:#1E1E2E;border-radius:12px;padding:20px;'
        f'margin:10px 0;border-left:5px solid {color}">'

        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">'
        f'<span style="background:{color};padding:3px 12px;border-radius:20px;'
        f'font-size:13px;font-weight:bold">{icon} {item["category"]}</span>'
        f'<span style="color:#AAA;font-size:12px">{item["source"]} &nbsp;|&nbsp; Score: {item["overall_score"]:.2f} {flag}</span>'
        f'</div>'

        f'<div style="font-size:17px;font-weight:bold;margin-bottom:10px;line-height:1.4">'
        f'{item["headline"]}</div>'

        f'<div style="font-size:14px;color:#CCC;line-height:1.7;margin-bottom:12px">'
        f'{item["summary"]}</div>'

        f'<a href="{item["url"]}" target="_blank" style="color:{color};font-size:13px;'
        f'text-decoration:none">🔗 Read full article</a>'
        f'</div>',
        unsafe_allow_html=True
    )


def main():
    st.set_page_config(
        page_title="NewsDigest",
        page_icon="📰",
        layout="wide"
    )

    # Header
    st.markdown(
        '<h1 style="text-align:center;font-size:42px">📰 NewsDigest</h1>'
        '<p style="text-align:center;color:#AAA;font-size:16px">'
        'AI-powered news summaries — stay informed in seconds</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    data = load_data()

    # ── Top Stats ─────────────────────────────────────────────────────────────
    categories = Counter(d["category"] for d in data)
    c_cols = st.columns(len(CATEGORY_ICONS))
    for i, (cat, icon) in enumerate(CATEGORY_ICONS.items()):
        count = categories.get(cat, 0)
        color = CATEGORY_COLORS.get(cat, "#DDD")
        c_cols[i].markdown(
            f'<div style="background:#1E1E2E;border-radius:10px;padding:12px;'
            f'text-align:center;border-top:3px solid {color}">'
            f'<div style="font-size:24px">{icon}</div>'
            f'<div style="font-weight:bold;font-size:14px">{cat}</div>'
            f'<div style="font-size:22px;font-weight:bold;color:{color}">{count}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ── Sidebar ───────────────────────────────────────────────────────────────
    st.sidebar.markdown("## 📰 NewsDigest")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate",
        ["🏠 Top Stories", "📂 By Category", "🔍 Search", "📊 Dataset Stats", "📤 Export Dataset"]
    )

    st.sidebar.markdown("---")
    quality_filter = st.sidebar.selectbox("Quality Filter", ["All", "Good only ✅", "Low only ⚠️"])
    sort_by        = st.sidebar.selectbox("Sort by", ["Default", "Highest Score", "Lowest Score"])

    # Apply filters
    filtered = data
    if quality_filter == "Good only ✅":
        filtered = [d for d in filtered if d["quality_flag"] == "GOOD"]
    elif quality_filter == "Low only ⚠️":
        filtered = [d for d in filtered if d["quality_flag"] == "LOW"]

    if sort_by == "Highest Score":
        filtered = sorted(filtered, key=lambda x: x["overall_score"], reverse=True)
    elif sort_by == "Lowest Score":
        filtered = sorted(filtered, key=lambda x: x["overall_score"])

    # ── Top Stories ───────────────────────────────────────────────────────────
    if page == "🏠 Top Stories":
        st.subheader(f"🏠 Top Stories — {len(filtered)} articles")
        for item in filtered:
            news_card(item)

    # ── By Category ───────────────────────────────────────────────────────────
    elif page == "📂 By Category":
        selected_cat = st.selectbox(
            "Select Category",
            list(CATEGORY_ICONS.keys())
        )
        cat_articles = [d for d in filtered if d["category"] == selected_cat]
        color = CATEGORY_COLORS.get(selected_cat, "#DDD")
        icon  = CATEGORY_ICONS.get(selected_cat, "📰")

        st.subheader(f"{icon} {selected_cat} — {len(cat_articles)} articles")
        if cat_articles:
            for item in cat_articles:
                news_card(item)
        else:
            st.info("No articles found for this category with current filters.")

    # ── Search ────────────────────────────────────────────────────────────────
    elif page == "🔍 Search":
        st.subheader("🔍 Search News")
        query = st.text_input("Search headlines and summaries", placeholder="e.g. AI, election, climate...")

        if query:
            results = [
                d for d in filtered
                if query.lower() in d["headline"].lower()
                or query.lower() in d["summary"].lower()
            ]
            st.markdown(f"**{len(results)} results for '{query}'**")
            if results:
                for item in results:
                    news_card(item)
            else:
                st.info("No results found. Try a different keyword.")
        else:
            st.info("Type something to search across all headlines and summaries.")

    # ── Dataset Stats ─────────────────────────────────────────────────────────
    elif page == "📊 Dataset Stats":
        st.subheader("📊 Dataset Statistics")

        good = sum(1 for d in data if d["quality_flag"] == "GOOD")
        low  = sum(1 for d in data if d["quality_flag"] == "LOW")
        avg  = sum(d["overall_score"] for d in data) / len(data)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Articles", len(data))
        c2.metric("✅ Good Quality", good)
        c3.metric("⚠️ Low Quality", low)
        c4.metric("Avg Score", f"{avg:.2f}")

        st.markdown("---")
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Quality by Category**")
            for cat, color in CATEGORY_COLORS.items():
                cat_items = [d for d in data if d["category"] == cat]
                if not cat_items:
                    continue
                cat_avg  = sum(d["overall_score"] for d in cat_items) / len(cat_items)
                cat_good = sum(1 for d in cat_items if d["quality_flag"] == "GOOD")
                icon = CATEGORY_ICONS.get(cat, "📰")
                st.markdown(
                    f'<div style="padding:10px;margin:5px 0;background:#1E1E2E;'
                    f'border-radius:8px;border-left:4px solid {color}">'
                    f'{icon} <b>{cat}</b> &nbsp;'
                    f'<span style="background:{color};padding:2px 8px;border-radius:10px;font-size:13px">'
                    f'Avg: {cat_avg:.2f}</span> &nbsp;'
                    f'<span style="font-size:13px;color:#AAA">✅ {cat_good}/{len(cat_items)}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        with col_b:
            st.markdown("**Score Dimensions (Average)**")
            dims = ["fluency", "relevance", "completeness", "conciseness", "diversity"]
            for dim in dims:
                avg_dim = sum(d["scores"][dim] for d in data) / len(data)
                width   = int(avg_dim * 200)
                st.markdown(
                    f'<div style="margin:8px 0">'
                    f'<small><b>{dim.capitalize()}</b></small><br>'
                    f'<div style="background:#333;border-radius:4px;height:12px;width:200px">'
                    f'<div style="background:#4ECDC4;width:{width}px;height:12px;border-radius:4px"></div>'
                    f'</div>'
                    f'<small style="color:#AAA">{avg_dim:.2f}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    # ── Export ────────────────────────────────────────────────────────────────
    elif page == "📤 Export Dataset":
        st.subheader("📤 Export Dataset")
        st.markdown("Download the summarization dataset for NLP/ML use.")

        export_choice = st.radio(
            "Which articles to export?",
            ["All articles", "Good quality only (≥0.65)"]
        )
        export_data = data if export_choice == "All articles" else \
                      [d for d in data if d["quality_flag"] == "GOOD"]

        st.info(f"Exporting {len(export_data)} articles")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📄 JSON")
            clean = [{
                "id":          d["id"],
                "category":    d["category"],
                "source":      d["source"],
                "headline":    d["headline"],
                "summary":     d["summary"],
                "url":         d["url"],
                "published_at": d["published_at"],
                "overall_score": d["overall_score"],
                "quality_flag": d["quality_flag"],
            } for d in export_data]
            st.download_button(
                "⬇️ Download JSON",
                data=json.dumps(clean, indent=2, ensure_ascii=False),
                file_name="newsdigest_dataset.json",
                mime="application/json",
                use_container_width=True
            )

        with col2:
            st.markdown("#### 📊 CSV")
            lines = ["id,category,source,headline,summary,overall_score,quality_flag,url"]
            for d in export_data:
                h = d["headline"].replace('"', '""')
                s = d["summary"].replace('"', '""')
                lines.append(
                    f'{d["id"]},{d["category"]},{d["source"]},"{h}","{s}",'
                    f'{d["overall_score"]},{d["quality_flag"]},{d["url"]}'
                )
            st.download_button(
                "⬇️ Download CSV",
                data="\n".join(lines),
                file_name="newsdigest_dataset.csv",
                mime="text/csv",
                use_container_width=True
            )


if __name__ == "__main__":
    main()
