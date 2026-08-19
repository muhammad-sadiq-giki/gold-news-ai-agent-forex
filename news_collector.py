import requests

url = "https://api.gdeltproject.org/api/v2/doc/doc"

params = {
    "query": '(gold OR XAU OR "Federal Reserve" OR Fed OR "interest rate" OR inflation OR tariffs OR Iran OR Israel OR "Middle East" OR "US dollar")',
    "mode": "artlist",
    "maxrecords": 10,
    "format": "json",
    "sort": "datedesc"
}

response = requests.get(url, params=params, timeout=30)

if response.status_code != 200:
    print("News request failed:", response.status_code)
    print(response.text)
    exit()

data = response.json()

articles = data.get("articles", [])

print("=" * 60)
print("LATEST GOLD-RELATED NEWS")
print("=" * 60)

for article in articles:
    title = article.get("title", "No title")
    url = article.get("url", "")
    source = article.get("domain", "Unknown")

    print()
    print("TITLE:", title)
    print("SOURCE:", source)
    print("URL:", url)
    print("-" * 60)

print()
print("Number of articles:", len(articles))
