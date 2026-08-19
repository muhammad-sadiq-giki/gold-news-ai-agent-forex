import requests
import time
import json
import os

NEWS_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

SEEN_FILE = "seen_news.json"

params = {
    "query": '("Federal Reserve" OR Fed OR "interest rate" OR inflation OR CPI OR tariffs OR Iran OR Israel OR "Middle East" OR "US dollar" OR sanctions OR war OR attack OR missile OR nuclear OR "banking crisis" OR "financial crisis")',
    "mode": "artlist",
    "maxrecords": 20,
    "format": "json",
    "sort": "datedesc"
}

HOT_KEYWORDS = [
    "war",
    "attack",
    "missile",
    "iran",
    "israel",
    "fed",
    "federal reserve",
    "emergency",
    "interest rate",
    "rate cut",
    "rate hike",
    "tariff",
    "sanctions",
    "nuclear",
    "ceasefire",
    "banking crisis",
    "financial crisis",
    "inflation",
    "cpi",
    "us dollar",
    "central bank",
    "trump"
]

headers = {
    "User-Agent": "GoldNewsAI/1.0 personal research bot"
}


# ============================================================
# LOAD PREVIOUSLY SEEN NEWS
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
print("GOLD NEWS AI")
print("=" * 70)

print()
print("Previously seen articles:", len(seen_news))


# ============================================================
# GET NEWS FROM GDELT
# ============================================================

response = None

for attempt in range(3):

    print()
    print(f"GDELT attempt {attempt + 1}/3...")

    try:

        response = requests.get(
            NEWS_URL,
            params=params,
            headers=headers,
            timeout=30
        )

    except requests.RequestException as error:

        print("Network error:")
        print(error)

        if attempt < 2:

            print("Waiting 30 seconds...")
            time.sleep(30)
            continue

        print("All attempts failed.")
        exit(0)


    # Successful request

    if response.status_code == 200:

        print("GDELT request successful.")
        break


    # Rate limit

    if response.status_code == 429:

        wait_time = 30 * (attempt + 1)

        print("GDELT returned HTTP 429.")
        print(f"Waiting {wait_time} seconds...")

        if attempt < 2:
            time.sleep(wait_time)

        continue


    # Other error

    print("GDELT request failed.")
    print("HTTP status:", response.status_code)
    print(response.text[:500])

    exit(0)


# ============================================================
# GDELT STILL UNAVAILABLE
# ============================================================

if response is None or response.status_code != 200:

    print()
    print("GDELT is currently unavailable or rate-limiting us.")
    print("No news processed during this run.")

    exit(0)


# ============================================================
# READ JSON
# ============================================================

try:

    data = response.json()

except ValueError:

    print("GDELT returned invalid JSON.")
    exit(0)


articles = data.get("articles", [])

print()
print("Articles received:", len(articles))


# ============================================================
# PROCESS ARTICLES
# ============================================================

new_articles = []
new_seen_urls = set()

for article in articles:

    title = article.get("title", "").strip()
    url = article.get("url", "").strip()
    source = article.get("domain", "Unknown")

    if not title or not url:
        continue


    # --------------------------------------------------------
    # Check whether we've already seen this article
    # --------------------------------------------------------

    if url in seen_news:

        continue


    # --------------------------------------------------------
    # New article
    # --------------------------------------------------------

    new_seen_urls.add(url)


    title_lower = title.lower()


    # --------------------------------------------------------
    # Find hot keywords
    # --------------------------------------------------------

    matched_keywords = [
        keyword
        for keyword in HOT_KEYWORDS
        if keyword in title_lower
    ]


    # --------------------------------------------------------
    # Only keep potentially important news
    # --------------------------------------------------------

    if matched_keywords:

        new_articles.append({
            "title": title,
            "url": url,
            "source": source,
            "keywords": matched_keywords
        })


# ============================================================
# DISPLAY NEW GOLD NEWS
# ============================================================

print()
print("=" * 70)
print("NEW POTENTIAL GOLD NEWS")
print("=" * 70)


if len(new_articles) == 0:

    print()
    print("No NEW potentially important Gold news found.")

else:

    for article in new_articles:

        print()
        print("🚨 NEW GOLD NEWS")
        print("-" * 70)

        print("TITLE:", article["title"])
        print("SOURCE:", article["source"])

        print(
            "KEYWORDS:",
            ", ".join(article["keywords"])
        )

        print("URL:", article["url"])

        print("-" * 70)


# ============================================================
# UPDATE MEMORY
# ============================================================

seen_news.update(new_seen_urls)


# Keep only the latest 500 URLs
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


print()
print("=" * 70)
print("MEMORY UPDATED")
print("=" * 70)

print("Total remembered URLs:", len(seen_news))

print()
print("Gold News AI filter finished.")
