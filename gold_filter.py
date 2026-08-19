import requests

NEWS_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

params = {
    "query": '(gold OR XAU OR "Federal Reserve" OR Fed OR "interest rate" OR inflation OR tariffs OR Iran OR Israel OR "Middle East" OR "US dollar" OR sanctions OR war OR attack)',
    "mode": "artlist",
    "maxrecords": 20,
    "format": "json",
    "sort": "datedesc"
}

# Words/events that may cause sudden gold volatility
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

response = requests.get(
    NEWS_URL,
    params=params,
    timeout=30
)

response.raise_for_status()

data = response.json()

articles = data.get("articles", [])

print("=" * 70)
print("POTENTIALLY IMPORTANT GOLD NEWS")
print("=" * 70)

found = 0

for article in articles:

    title = article.get("title", "")
    url = article.get("url", "")
    source = article.get("domain", "Unknown")

    title_lower = title.lower()

    matched_keywords = [
        word for word in HOT_KEYWORDS
        if word in title_lower
    ]

    if matched_keywords:

        found += 1

        print()
        print("🚨 POSSIBLE GOLD IMPACT")
        print("TITLE:", title)
        print("SOURCE:", source)
        print("KEYWORDS:", ", ".join(matched_keywords))
        print("URL:", url)
        print("-" * 70)

print()
print("Potentially important articles:", found)
