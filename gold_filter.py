import requests
import time

NEWS_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

# News topics that can potentially cause sudden moves in gold (XAU/USD)
params = {
    "query": '("Federal Reserve" OR Fed OR "interest rate" OR inflation OR CPI OR tariffs OR Iran OR Israel OR "Middle East" OR "US dollar" OR sanctions OR war OR attack OR missile OR nuclear OR "banking crisis" OR "financial crisis")',
    "mode": "artlist",
    "maxrecords": 20,
    "format": "json",
    "sort": "datedesc"
}

# Keywords that may indicate a potentially important event
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

print("=" * 70)
print("GOLD NEWS AI - NEWS COLLECTOR")
print("=" * 70)

# ---------------------------------------------------------
# Request news from GDELT
# ---------------------------------------------------------

response = None

for attempt in range(3):

    print()
    print(f"Attempt {attempt + 1}/3...")

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
            print("Waiting 30 seconds before retrying...")
            time.sleep(30)
            continue

        print("All attempts failed.")
        exit(0)

    # Successful request
    if response.status_code == 200:
        print("GDELT request successful.")
        break

    # Rate limited
    if response.status_code == 429:

        wait_time = 30 * (attempt + 1)

        print("GDELT returned HTTP 429.")
        print("Too many requests / temporary rate limit.")
        print(f"Waiting {wait_time} seconds before retrying...")

        if attempt < 2:
            time.sleep(wait_time)

        continue

    # Other HTTP error
    print("GDELT request failed.")
    print("HTTP status:", response.status_code)
    print(response.text[:500])

    exit(0)


# ---------------------------------------------------------
# If GDELT is still unavailable
# ---------------------------------------------------------

if response is None or response.status_code != 200:

    print()
    print("=" * 70)
    print("GDELT IS CURRENTLY RATE LIMITING THE REQUEST")
    print("=" * 70)
    print()
    print("No news was processed this time.")
    print("The next scheduled run will try again.")

    # Exit 0 so GitHub doesn't mark the workflow as failed.
    exit(0)


# ---------------------------------------------------------
# Read JSON response
# ---------------------------------------------------------

try:

    data = response.json()

except ValueError:

    print("GDELT returned invalid JSON.")
    print(response.text[:500])
    exit(0)


articles = data.get("articles", [])

print()
print("=" * 70)
print("LATEST GOLD-RELATED NEWS")
print("=" * 70)

print()
print("Articles received:", len(articles))


# ---------------------------------------------------------
# Filter potentially important news
# ---------------------------------------------------------

found = 0

for article in articles:

    title = article.get("title", "").strip()
    url = article.get("url", "")
    source = article.get("domain", "Unknown")

    if not title:
        continue

    title_lower = title.lower()

    # Find hot keywords in the headline
    matched_keywords = [
        keyword
        for keyword in HOT_KEYWORDS
        if keyword in title_lower
    ]

    if matched_keywords:

        found += 1

        print()
        print("🚨 POSSIBLE GOLD IMPACT")
        print("-" * 70)
        print("TITLE:", title)
        print("SOURCE:", source)
        print("KEYWORDS:", ", ".join(matched_keywords))
        print("URL:", url)
        print("-" * 70)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print()
print("=" * 70)
print("FILTER SUMMARY")
print("=" * 70)

print("Total articles received:", len(articles))
print("Potentially important:", found)

if found == 0:

    print()
    print("No potentially important Gold news found.")

else:

    print()
    print("🚨 Potential Gold-moving news detected.")

print()
print("Gold News AI filter finished.")
