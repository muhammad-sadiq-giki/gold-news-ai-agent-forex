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

    # ========================================================
    # GOLD PRICE / MARKET MOVEMENT
    # ========================================================

    "gold leaps": 60,
    "gold jumps": 60,
    "gold surges": 60,
    "gold spikes": 60,
    "gold plunges": 60,
    "gold crashes": 70,
    "gold tumbles": 50,
    "gold falls": 35,
    "gold rises": 30,
    "gold rebounds": 30,

    "gold gains": 25,
    "gold rally": 40,
    "gold rallies": 40,

    "$100": 50,
    "$50": 30,

    "record high": 45,
    "all-time high": 50,

    # ========================================================
    # US TREASURY / BONDS / YIELDS
    # ========================================================

    "treasury bond": 30,
    "treasury bonds": 30,
    "bond yields": 30,
    "bond yield": 30,
    "treasury yield": 30,
    "treasury yields": 30,

    "yield falls": 35,
    "yields fall": 35,
    "yield rises": 30,
    "yields rise": 30,

    "bond buybacks": 50,
    "treasury buybacks": 50,

    # ========================================================
    # FEDERAL RESERVE
    # ========================================================

    "federal reserve": 30,
    "fed": 20,
    "fed meeting": 35,
    "fed minutes": 35,
    "fed decision": 50,

    "interest rate": 25,
    "interest rates": 25,

    "rate cut": 45,
    "rate cuts": 45,

    "rate hike": 45,
    "rate hikes": 45,

    "emergency rate": 60,
    "emergency meeting": 60,

    "quantitative easing": 50,
    "quantitative tightening": 40,

    # ========================================================
    # US ECONOMIC DATA
    # ========================================================

    "cpi": 40,
    "inflation": 25,

    "jobs report": 35,
    "nonfarm payroll": 45,
    "payrolls": 35,

    "unemployment": 30,
    "unemployment rate": 35,

    "ppi": 35,
    "retail sales": 25,
    "gdp": 30,

    # ========================================================
    # GEOPOLITICAL EVENTS
    # ========================================================

    "war": 45,
    "attack": 45,
    "missile": 50,
    "missile strike": 55,
    "airstrike": 50,

    "invasion": 60,
    "nuclear": 60,

    "iran": 25,
    "israel": 25,

    "middle east": 30,

    "ceasefire": 35,
    "peace deal": 25,

    "sanctions": 30,

    "military": 30,
    "military strike": 50,

    # ========================================================
    # TRADE / TARIFFS
    # ========================================================

    "tariff": 25,
    "tariffs": 25,

    "trade war": 45,
    "trade deal": 25,

    # ========================================================
    # FINANCIAL CRISIS
    # ========================================================

    "banking crisis": 60,
    "bank failure": 60,
    "bank collapse": 70,

    "financial crisis": 60,
    "market crash": 60,

    # ========================================================
    # US DOLLAR
    # ========================================================

    "us dollar": 20,
    "dollar falls": 30,
    "dollar drops": 35,
    "dollar plunges": 50,

    "dollar rises": 20,
    "dollar strengthens": 25,

    # ========================================================
    # CENTRAL BANKS
    # ========================================================

    "central bank": 20,
    "central banks": 20,

    "ecb": 20,
    "boj": 20,
    "bank of japan": 25,
    "bank of england": 20,

    # ========================================================
    # IMPORTANT POLITICAL FIGURES
    # ========================================================

    "trump": 10
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
