import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import json
import os

RSS_URL = (
    "https://news.google.com/rss/search?"
    "q=(gold+OR+XAU+OR+%22Federal+Reserve%22+OR+Fed+OR+"
    "Iran+OR+Israel+OR+%22Middle+East%22+OR+%22US+dollar%22+"
    "OR+tariffs+OR+inflation+OR+%22interest+rate%22)"
    "&hl=en-US"
    "&gl=US"
    "&ceid=US:en"
)

SEEN_FILE = "seen_news.json"

headers = {
    "User-Agent": "Mozilla/5.0 GoldNewsAI/1.0"
}

MAX_AGE_HOURS = 2


# ============================================================
# GOLD IMPACT KEYWORDS
# ============================================================

HOT_EVENTS = {
    "war": 40,
    "attack": 40,
    "missile": 45,
    "invasion": 50,
    "iran": 25,
    "israel": 25,
    "nuclear": 50,
    "ceasefire": 30,
    "sanctions": 25,

    "federal reserve": 30,
    "fed": 25,
    "interest rate": 25,
    "rate cut": 40,
    "rate hike": 40,
    "emergency rate": 50,

    "inflation": 20,
    "cpi": 35,
    "jobs report": 30,
    "nonfarm payroll": 40,
    "unemployment": 25,

    "tariff": 25,
    "trade war": 40,

    "banking crisis": 50,
    "financial crisis": 50,

    "us dollar": 20,
    "dollar falls": 25,
    "dollar rises": 20,

    "central bank": 20,
    "trump": 15
}


# ============================================================
# LOAD MEMORY
# ============================================================

if os.path.exists(SEEN_FILE):

    try:

        with open(
            SEEN_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            seen_news = set(json.load(file))

    except Exception:

        print("Could not read seen_news.json.")

        seen_news = set()

else:

    seen_news = set()


print("=" * 70)
print("GOLD BREAKING NEWS AI")
print("=" * 70)

print()
print("Previously seen articles:", len(seen_news))


# ============================================================
# DOWNLOAD RSS
# ============================================================

try:

    response = requests.get(
        RSS_URL,
        headers=headers,
        timeout=30
    )

    print("HTTP status:", response.status_code)

    response.raise_for_status()

except requests.RequestException as error:

    print("RSS request failed:")
    print(error)

    exit(1)


# ============================================================
# PARSE RSS
# ============================================================

try:

    root = ET.fromstring(response.content)

except ET.ParseError as error:

    print("Could not parse RSS:")
    print(error)

    exit(1)


items = root.findall(".//item")

print("Total RSS articles:", len(items))


# ============================================================
# TIME FILTER
# ============================================================

now = datetime.now(timezone.utc)

cutoff_time = now - timedelta(
    hours=MAX_AGE_HOURS
)


# ============================================================
# PROCESS ARTICLES
# ============================================================

new_articles = []

new_urls = set()


for item in items:

    title = item.findtext(
        "title",
        ""
    ).strip()

    link = item.findtext(
        "link",
        ""
    ).strip()

    pub_date = item.findtext(
        "pubDate",
        ""
    ).strip()


    if not title or not link or not pub_date:
        continue


    # --------------------------------------------------------
    # Parse publication date
    # --------------------------------------------------------

    try:

        published = parsedate_to_datetime(
            pub_date
        )

        if published.tzinfo is None:

            published = published.replace(
                tzinfo=timezone.utc
            )

    except Exception:

        continue


    # --------------------------------------------------------
    # Ignore old articles
    # --------------------------------------------------------

    if published < cutoff_time:

        continue


    # --------------------------------------------------------
    # Ignore previously seen articles
    # --------------------------------------------------------

    if link in seen_news:

        continue


    # --------------------------------------------------------
    # Ignore duplicates in current run
    # --------------------------------------------------------

    if link in new_urls:

        continue


    new_urls.add(link)


    # --------------------------------------------------------
    # Calculate Gold Impact Score
    # --------------------------------------------------------

    title_lower = title.lower()

    score = 0

    matched_events = []


    for event, points in HOT_EVENTS.items():

        if event in title_lower:

            score += points

            matched_events.append(event)


    # Maximum score = 100

    score = min(score, 100)


    # --------------------------------------------------------
    # Determine impact level
    # --------------------------------------------------------

    if score >= 80:

        impact = "EXTREME"

    elif score >= 60:

        impact = "HIGH"

    elif score >= 30:

        impact = "MEDIUM"

    else:

        impact = "LOW"


    new_articles.append({
        "title": title,
        "url": link,
        "published": published.isoformat(),
        "score": score,
        "impact": impact,
        "events": matched_events
    })


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 70)
print("NEW GOLD NEWS + IMPACT SCORE")
print("=" * 70)

print()
print("New articles:", len(new_articles))


for article in new_articles:

    print()
    print("NEWS")
    print("-" * 70)

    print(
        "TITLE:",
        article["title"]
    )

    print(
        "PUBLISHED:",
        article["published"]
    )

    print(
        "IMPACT SCORE:",
        article["score"],
        "/ 100"
    )

    print(
        "IMPACT LEVEL:",
        article["impact"]
    )

    print(
        "EVENTS:",
        ", ".join(article["events"])
        if article["events"]
        else "None"
    )

    print(
        "URL:",
        article["url"]
    )

    print("-" * 70)


# ============================================================
# UPDATE MEMORY
# ============================================================

for article in new_articles:

    seen_news.add(
        article["url"]
    )


# Keep only the latest 500 URLs

if len(seen_news) > 500:

    seen_news = set(
        list(seen_news)[-500:]
    )


with open(
    SEEN_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        list(seen_news),
        file,
        indent=2
    )


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(
    "Previously seen:",
    len(seen_news)
)

print(
    "New articles:",
    len(new_articles)
)

high_count = sum(
    1
    for article in new_articles
    if article["score"] >= 60
)

print(
    "High/Extreme impact:",
    high_count
)

print()
print("Gold News AI finished.")
