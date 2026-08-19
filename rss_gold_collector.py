import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

RSS_URL = (
    "https://news.google.com/rss/search?"
    "q=(gold+OR+XAU+OR+%22Federal+Reserve%22+OR+Fed+OR+"
    "Iran+OR+Israel+OR+%22Middle+East%22+OR+%22US+dollar%22+"
    "OR+tariffs+OR+inflation+OR+%22interest+rate%22)"
    "&hl=en-US"
    "&gl=US"
    "&ceid=US:en"
)

headers = {
    "User-Agent": "Mozilla/5.0 GoldNewsAI/1.0"
}

# Only consider news from the last 2 hours
MAX_AGE_HOURS = 2


print("=" * 70)
print("GOLD BREAKING NEWS COLLECTOR")
print("=" * 70)


# ---------------------------------------------------------
# Download RSS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Parse RSS
# ---------------------------------------------------------

try:

    root = ET.fromstring(response.content)

except ET.ParseError as error:

    print("Could not parse RSS:")
    print(error)
    exit(1)


items = root.findall(".//item")

print("Total RSS articles:", len(items))


# ---------------------------------------------------------
# Current time
# ---------------------------------------------------------

now = datetime.now(timezone.utc)

cutoff_time = now - timedelta(hours=MAX_AGE_HOURS)


# ---------------------------------------------------------
# Process articles
# ---------------------------------------------------------

recent_articles = []


for item in items:

    title = item.findtext("title", "").strip()
    link = item.findtext("link", "").strip()
    pub_date = item.findtext("pubDate", "").strip()


    if not title or not link or not pub_date:
        continue


    # -----------------------------------------------------
    # Convert publication date
    # -----------------------------------------------------

    try:

        published = parsedate_to_datetime(pub_date)

        if published.tzinfo is None:
            published = published.replace(
                tzinfo=timezone.utc
            )

    except Exception:

        continue


    # -----------------------------------------------------
    # Ignore old news
    # -----------------------------------------------------

    if published < cutoff_time:
        continue


    # -----------------------------------------------------
    # Save recent article
    # -----------------------------------------------------

    recent_articles.append({
        "title": title,
        "url": link,
        "published": published.isoformat()
    })


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print()
print("=" * 70)
print("RECENT GOLD-RELATED NEWS")
print("=" * 70)

print()
print("News from last", MAX_AGE_HOURS, "hours:", len(recent_articles))


for article in recent_articles:

    print()
    print("TITLE:", article["title"])
    print("PUBLISHED:", article["published"])
    print("URL:", article["url"])
    print("-" * 70)


print()
print("=" * 70)
print("COLLECTOR FINISHED")
print("=" * 70)
