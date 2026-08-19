import requests
import xml.etree.ElementTree as ET

RSS_URL = (
    "https://news.google.com/rss/search?"
    "q=gold+OR+XAU+OR+Federal+Reserve+OR+Iran+OR+Israel"
    "&hl=en-US"
    "&gl=US"
    "&ceid=US:en"
)

headers = {
    "User-Agent": "Mozilla/5.0 GoldNewsAI/1.0"
}

print("=" * 70)
print("GOLD NEWS RSS TEST")
print("=" * 70)

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

try:
    root = ET.fromstring(response.content)

except ET.ParseError as error:
    print("Could not read RSS data:")
    print(error)
    exit(1)

items = root.findall(".//item")

print()
print("Articles received:", len(items))
print("=" * 70)

for item in items[:10]:

    title = item.findtext("title", "")
    link = item.findtext("link", "")
    pub_date = item.findtext("pubDate", "")

    print()
    print("TITLE:", title)
    print("DATE:", pub_date)
    print("URL:", link)
    print("-" * 70)

print()
print("RSS test completed.")
