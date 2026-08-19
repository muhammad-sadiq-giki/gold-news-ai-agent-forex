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
# LOAD MEMORY
# ============================================================

if os.path.exists(SEEN_FILE):
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as file:
            seen_news = set(json.load(file))
    except Exception:
        print("Could not read seen_news.json.")
        seen_news = set()
else:
    seen_news = set()


print("=" * 70)
print("GOLD BREAKING NEWS COLLECTOR")
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

cutoff_time = now - timedelta(hours=MAX_AGE_HOURS)


# ============================================================
# PROCESS ARTICLES
# ============================================================

new_articles = []
new_urls = set()

for item in items:

    title = item.findtext("title", "").strip()
    link = item.findtext("link", "").strip()
    pub_date = item.findtext("pubDate", "").strip()

    if not title or not link or not pub_date:
        continue

    try:
        published = parsedate_to_datetime(pub_date)

        if published.tzinfo is None:
            published = published.replace(
                tzinfo=timezone.utc
            )

    except Exception:
        continue

    # Ignore articles older than 2 hours
    if published < cutoff_time:
        continue

    # Ignore articles already processed
    if link in seen_news:
        continue

    # Avoid duplicates in this run
    if link in new_urls:
        continue

    new_urls.add(link)

    new_articles.append({
        "title": title,
        "url": link,
        "published": published.isoformat()
    })


# ============================================================
# DISPLAY NEW ARTICLES
# ============================================================

print()
print("=" * 70)
print("NEW RECENT GOLD NEWS")
print("=" * 70)

print()
print("New articles:", len(new_articles))


for article in new_articles:

    print()
    print("🚨 NEW ARTICLE")
    print("-" * 70)

    print("TITLE:", article["title"])
    print("PUBLISHED:", article["published"])
    print("URL:", article["url"])

    print("-" * 70)


# ============================================================
# UPDATE MEMORY
# ============================================================

for article in new_articles:
    seen_news.add(article["url"])


# Keep memory manageable
if len(seen_news) > 500:
    seen_news = set(list(seen_news)[-500:])


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
print("MEMORY UPDATED")
print("=" * 70)

print("Previously seen + new:", len(seen_news))

print()
print("Gold Breaking News Collector finished.")
