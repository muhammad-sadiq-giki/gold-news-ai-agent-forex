import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import json
import os
import re
import html


# ============================================================
# CONFIGURATION
# ============================================================

GOOGLE_RSS_URL = (
    "https://news.google.com/rss/search?"
    "q=(gold+OR+XAU+OR+%22Federal+Reserve%22+OR+Fed+OR+"
    "Iran+OR+Israel+OR+%22Middle+East%22+OR+%22US+dollar%22+"
    "OR+tariffs+OR+inflation+OR+%22interest+rate%22)"
    "&hl=en-US"
    "&gl=US"
    "&ceid=US:en"
)

FOREX_FACTORY_URL = "https://www.forexfactory.com/news"

SEEN_FILE = "seen_news.json"

MAX_AGE_HOURS = 2

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ============================================================
# API SECRETS
# ============================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


# ============================================================
# GROQ CONFIGURATION
# ============================================================

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

GROQ_MODEL = "openai/gpt-oss-20b"


# ============================================================
# GOLD IMPACT KEYWORDS
# ============================================================

HOT_EVENTS = {

    # GOLD
    "gold leaps": 60,
    "gold jumps": 60,
    "gold surges": 60,
    "gold spikes": 60,
    "gold soars": 60,
    "gold rallies": 40,
    "gold rally": 40,
    "gold plunges": 70,
    "gold crashes": 70,
    "gold tumbles": 50,
    "gold falls": 35,
    "gold rises": 30,
    "gold rebounds": 30,
    "gold gains": 25,
    "gold price": 20,
    "gold prices": 20,
    "xauusd": 35,
    "$100": 50,
    "$50": 30,
    "record high": 45,
    "all-time high": 50,
    "all time high": 50,

    # TREASURY / BONDS
    "treasury bond": 30,
    "treasury bonds": 30,
    "bond yields": 30,
    "bond yield": 30,
    "treasury yield": 30,
    "treasury yields": 30,
    "yield falls": 35,
    "yields fall": 35,
    "yield drops": 35,
    "yields drop": 35,
    "yield rises": 30,
    "yields rise": 30,
    "yield jumps": 35,
    "yields jump": 35,
    "bond buybacks": 50,
    "treasury buybacks": 50,
    "treasury buyback": 50,
    "buyback": 25,
    "buybacks": 25,

    # FED
    "federal reserve": 30,
    "fed": 20,
    "fed meeting": 35,
    "fed minutes": 35,
    "fomc": 35,
    "fomc minutes": 45,
    "fed decision": 50,
    "interest rate": 25,
    "interest rates": 25,
    "rate cut": 45,
    "rate cuts": 45,
    "rate hike": 45,
    "rate hikes": 45,
    "rate increase": 40,
    "rate increases": 40,
    "emergency rate": 60,
    "emergency meeting": 60,
    "quantitative easing": 50,
    "quantitative tightening": 40,

    # ECONOMIC DATA
    "cpi": 40,
    "inflation": 25,
    "jobs report": 35,
    "nonfarm payroll": 45,
    "nonfarm payrolls": 45,
    "payrolls": 35,
    "unemployment": 30,
    "unemployment rate": 35,
    "ppi": 35,
    "retail sales": 25,
    "gdp": 30,
    "economic data": 20,

    # GEOPOLITICAL
    "war": 45,
    "attack": 45,
    "attacks": 45,
    "missile": 50,
    "missile strike": 55,
    "airstrike": 50,
    "air strike": 50,
    "invasion": 60,
    "nuclear": 60,
    "iran": 25,
    "israel": 25,
    "middle east": 30,
    "gulf": 20,
    "hormuz": 35,
    "ceasefire": 35,
    "peace deal": 25,
    "sanctions": 30,
    "military": 30,
    "military strike": 50,
    "escalation": 40,

    # TRADE
    "tariff": 25,
    "tariffs": 25,
    "trade war": 45,
    "trade deal": 25,

    # FINANCIAL CRISIS
    "banking crisis": 60,
    "bank failure": 60,
    "bank collapse": 70,
    "financial crisis": 60,
    "market crash": 60,
    "market collapse": 60,

    # US DOLLAR
    "us dollar": 20,
    "dollar falls": 30,
    "dollar drops": 35,
    "dollar plunges": 50,
    "dollar weakens": 40,
    "dollar rises": 20,
    "dollar strengthens": 25,
    "dxy": 25,

    # CENTRAL BANKS
    "central bank": 20,
    "central banks": 20,
    "ecb": 20,
    "boj": 20,
    "bank of japan": 25,
    "bank of england": 20,

    # POLITICS
    "trump": 10,
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

            seen_news = set(
                json.load(file)
            )

    except Exception:

        print("Could not read seen_news.json.")

        seen_news = set()

else:

    seen_news = set()


# ============================================================
# START
# ============================================================

print("=" * 70)
print("GOLD NEWS AI MULTI-SOURCE COLLECTOR")
print("=" * 70)

print()

print(
    "Previously seen articles:",
    len(seen_news)
)

print()

print("Sources:")
print("1. Google News RSS")
print("2. Forex Factory News")
print()


# ============================================================
# HELPER: PARSE FOREX FACTORY RELATIVE TIME
# ============================================================

def parse_forex_factory_time(text):

    if not text:
        return None

    text = text.lower().strip()

    now = datetime.now(timezone.utc)

    # --------------------------------------------------------
    # minutes
    # --------------------------------------------------------

    match = re.search(
        r"(\d+)\s*(?:min|mins|minute|minutes)\s*ago",
        text
    )

    if match:

        minutes = int(match.group(1))

        return now - timedelta(
            minutes=minutes
        )

    # --------------------------------------------------------
    # hours
    # --------------------------------------------------------

    match = re.search(
        r"(\d+)\s*(?:hr|hrs|hour|hours)\s*ago",
        text
    )

    if match:

        hours = int(match.group(1))

        return now - timedelta(
            hours=hours
        )

    # --------------------------------------------------------
    # days
    # --------------------------------------------------------

    match = re.search(
        r"(\d+)\s*(?:day|days)\s*ago",
        text
    )

    if match:

        days = int(match.group(1))

        return now - timedelta(
            days=days
        )

    # --------------------------------------------------------
    # yesterday
    # --------------------------------------------------------

    if "yesterday" in text:

        return now - timedelta(
            days=1
        )

    return None


# ============================================================
# GOOGLE NEWS COLLECTOR
# ============================================================

def collect_google_news():

    print("=" * 70)
    print("COLLECTING GOOGLE NEWS")
    print("=" * 70)

    articles = []

    try:

        response = requests.get(
            GOOGLE_RSS_URL,
            headers=HEADERS,
            timeout=30
        )

        print(
            "Google News HTTP status:",
            response.status_code
        )

        response.raise_for_status()

    except requests.RequestException as error:

        print()
        print("Google News request failed:")
        print(error)

        return articles

    try:

        root = ET.fromstring(
            response.content
        )

    except ET.ParseError as error:

        print()
        print("Could not parse Google RSS:")
        print(error)

        return articles

    items = root.findall(".//item")

    print(
        "Google News articles:",
        len(items)
    )

    now = datetime.now(
        timezone.utc
    )

    cutoff_time = now - timedelta(
        hours=MAX_AGE_HOURS
    )

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

        if not title or not link:

            continue

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

        if published < cutoff_time:

            continue

        articles.append({

            "title": title,

            "url": link,

            "published": published,

            "source": "Google News",

            "description": ""

        })

    return articles


# ============================================================
# FOREX FACTORY COLLECTOR
# ============================================================

def collect_forex_factory():

    print()
    print("=" * 70)
    print("COLLECTING FOREX FACTORY NEWS")
    print("=" * 70)

    articles = []

    try:

        response = requests.get(
            FOREX_FACTORY_URL,
            headers=HEADERS,
            timeout=30
        )

        print(
            "Forex Factory HTTP status:",
            response.status_code
        )

        response.raise_for_status()

    except requests.RequestException as error:

        print()
        print("Forex Factory request failed:")
        print(error)

        return articles

    try:

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

    except Exception as error:

        print()
        print("Could not parse Forex Factory:")
        print(error)

        return articles

    now = datetime.now(
        timezone.utc
    )

    cutoff_time = now - timedelta(
        hours=MAX_AGE_HOURS
    )

    seen_ff_urls = set()

    # ========================================================
    # FIND NEWS ARTICLE LINKS
    # ========================================================

    for anchor in soup.find_all(
        "a",
        href=True
    ):

        title = anchor.get_text(
            " ",
            strip=True
        )

        href = anchor.get(
            "href",
            ""
        ).strip()

        if not title:

            continue

        if not href:

            continue

        # Forex Factory news article links
        if "/news/" not in href:

            continue

        # Ignore the main news page itself
        if href.rstrip("/") == "/news":

            continue

        # ----------------------------------------------------
        # Convert relative URL
        # ----------------------------------------------------

        if href.startswith("/"):

            url = (
                "https://www.forexfactory.com"
                + href
            )

        elif href.startswith("http"):

            url = href

        else:

            continue

        # ----------------------------------------------------
        # Avoid duplicate links
        # ----------------------------------------------------

        if url in seen_ff_urls:

            continue

        seen_ff_urls.add(url)

        # ----------------------------------------------------
        # Ignore navigation / irrelevant links
        # ----------------------------------------------------

        lower_title = title.lower()

        ignored_titles = {

            "news",
            "latest stories",
            "hot stories",
            "search news",
            "submit news",
            "news alerts",
            "subscribe",
            "login",
            "create account",
        }

        if lower_title in ignored_titles:

            continue

        if len(title) < 10:

            continue

        # ----------------------------------------------------
        # Get surrounding text
        # ----------------------------------------------------

        parent = anchor.parent

        surrounding_text = ""

        if parent:

            surrounding_text = parent.get_text(
                " ",
                strip=True
            )

        # Sometimes the useful time is several levels
        # above the anchor.

        current = parent

        for _ in range(4):

            if current:

                text = current.get_text(
                    " ",
                    strip=True
                )

                if len(text) > len(
                    surrounding_text
                ):

                    surrounding_text = text

                current = current.parent

        # ----------------------------------------------------
        # Parse relative publication time
        # ----------------------------------------------------

        published = parse_forex_factory_time(
            surrounding_text
        )

        if published is None:

            continue

        if published < cutoff_time:

            continue

        # ----------------------------------------------------
        # Extract a short description
        # ----------------------------------------------------

        description = surrounding_text

        description = description.replace(
            title,
            "",
            1
        ).strip()

        # Limit description size
        if len(description) > 1000:

            description = description[:1000]

        articles.append({

            "title": html.unescape(title),

            "url": url,

            "published": published,

            "source": "Forex Factory",

            "description": html.unescape(
                description
            )

        })

    # --------------------------------------------------------
    # Remove duplicate titles
    # --------------------------------------------------------

    unique_articles = []

    seen_titles = set()

    for article in articles:

        title_key = article["title"].lower().strip()

        if title_key in seen_titles:

            continue

        seen_titles.add(
            title_key
        )

        unique_articles.append(
            article
        )

    print(
        "Forex Factory recent articles:",
        len(unique_articles)
    )

    return unique_articles


# ============================================================
# COLLECT FROM BOTH SOURCES
# ============================================================

google_articles = collect_google_news()

forex_factory_articles = collect_forex_factory()

all_articles = (
    google_articles
    + forex_factory_articles
)


print()
print("=" * 70)
print("COMBINED NEWS")
print("=" * 70)

print(
    "Google News:",
    len(google_articles)
)

print(
    "Forex Factory:",
    len(forex_factory_articles)
)

print(
    "Combined:",
    len(all_articles)
)


# ============================================================
# DISCORD FUNCTION
# ============================================================

def send_discord_alert(
    article,
    ai_result,
    keyword_score,
    matched_events
):

    if not DISCORD_WEBHOOK:

        print()
        print(
            "ERROR: DISCORD_WEBHOOK is missing."
        )

        return False

    title = article["title"]

    url = article["url"]

    source = article["source"]

    direction = ai_result.get(
        "gold_direction",
        "UNCLEAR"
    )

    impact = ai_result.get(
        "impact",
        "UNKNOWN"
    )

    confidence = ai_result.get(
        "confidence",
        0
    )

    reason = ai_result.get(
        "reason",
        ""
    )

    message = (
        "🚨 **GOLD BREAKING NEWS ALERT** 🚨\n\n"

        f"**Source:** {source}\n"

        f"**News:** {title}\n\n"

        f"**Gold Direction:** {direction}\n"

        f"**AI Impact:** {impact}\n"

        f"**AI Confidence:** {confidence}%\n"

        f"**Keyword Score:** {keyword_score}/100\n"

        f"**Matched Events:** "
        f"{', '.join(matched_events) if matched_events else 'None'}\n\n"

        f"**Why:** {reason}\n\n"

        f"🔗 {url}"
    )

    payload = {
        "content": message
    }

    try:

        response = requests.post(
            DISCORD_WEBHOOK,
            json=payload,
            timeout=30
        )

        if response.status_code in (
            200,
            204
        ):

            print()
            print(
                "Discord alert sent successfully."
            )

            return True

        print()

        print(
            "Discord HTTP status:",
            response.status_code
        )

        print(
            "Discord response:",
            response.text
        )

        return False

    except Exception as error:

        print()

        print(
            "Discord alert failed:",
            error
        )

        return False


# ============================================================
# GROQ AI FUNCTION
# ============================================================

def analyze_with_ai(
    title,
    source,
    description
):

    if not GROQ_API_KEY:

        print()
        print(
            "ERROR: GROQ_API_KEY is missing."
        )

        return None

    prompt = f"""
You are a professional financial news analyst specializing
in Gold (XAU/USD).

Analyze the following financial news.

SOURCE:
{source}

HEADLINE:
{title}

DESCRIPTION:
{description}

Determine whether this news could cause a sudden meaningful
movement in Gold/XAUUSD.

Pay particular attention to:

- Federal Reserve decisions
- FOMC minutes
- interest rates
- Treasury yields
- Treasury bond buybacks
- US dollar
- inflation
- CPI
- jobs data
- geopolitical conflicts
- Iran
- Israel
- Middle East
- tariffs
- financial crises
- major gold price movements

IMPORTANT:

Do not assume that every geopolitical or political headline
will move gold significantly.

Consider whether the event is actually capable of causing
a meaningful market reaction.

Return ONLY valid JSON:

{{
  "is_market_moving": true,
  "gold_direction": "BULLISH",
  "impact": "EXTREME",
  "confidence": 90,
  "reason": "Short explanation."
}}

Rules:

is_market_moving:
true or false

gold_direction:
"BULLISH", "BEARISH", or "UNCLEAR"

impact:
"LOW", "MEDIUM", "HIGH", or "EXTREME"

confidence:
integer from 0 to 100

reason:
maximum 2 short sentences.

Do not give trading advice.
"""

    headers = {

        "Authorization":
            f"Bearer {GROQ_API_KEY}",

        "Content-Type":
            "application/json"

    }

    payload = {

        "model":
            GROQ_MODEL,

        "messages": [

            {
                "role": "user",
                "content": prompt
            }

        ],

        "temperature":
            0,

        "response_format": {
            "type": "json_object"
        }

    }

    try:

        response = requests.post(

            GROQ_URL,

            headers=headers,

            json=payload,

            timeout=60

        )

        if response.status_code != 200:

            print()

            print(
                "Groq HTTP status:",
                response.status_code
            )

            print(
                "Groq response:",
                response.text
            )

            return None

        result = response.json()

        content = (
            result[
                "choices"
            ][0][
                "message"
            ][
                "content"
            ]
        )

        return json.loads(
            content
        )

    except Exception as error:

        print()

        print(
            "AI analysis failed:",
            error
        )

        return None


# ============================================================
# PROCESS ARTICLES
# ============================================================

new_articles = []

new_urls = set()

seen_titles = set()


for article in all_articles:

    title = article["title"].strip()

    link = article["url"].strip()

    published = article["published"]

    source = article["source"]

    description = article.get(
        "description",
        ""
    )

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    if not title or not link:

        continue

    # --------------------------------------------------------
    # Previously seen
    # --------------------------------------------------------

    if link in seen_news:

        continue

    # --------------------------------------------------------
    # Duplicate during this run
    # --------------------------------------------------------

    if link in new_urls:

        continue

    # --------------------------------------------------------
    # Duplicate title across sources
    # --------------------------------------------------------

    title_key = title.lower().strip()

    if title_key in seen_titles:

        continue

    seen_titles.add(
        title_key
    )

    new_urls.add(
        link
    )

    # ========================================================
    # KEYWORD SCORE
    # ========================================================

    title_lower = title.lower()

    score = 0

    matched_events = []

    for event, points in HOT_EVENTS.items():

        if event in title_lower:

            score += points

            matched_events.append(
                event
            )

    # --------------------------------------------------------
    # Cap at 100
    # --------------------------------------------------------

    score = min(
        score,
        100
    )

    # ========================================================
    # KEYWORD IMPACT
    # ========================================================

    if score >= 80:

        keyword_impact = "EXTREME"

    elif score >= 60:

        keyword_impact = "HIGH"

    elif score >= 30:

        keyword_impact = "MEDIUM"

    else:

        keyword_impact = "LOW"

    # ========================================================
    # AI ANALYSIS
    # ========================================================

    ai_result = None

    if score >= 30:

        print()
        print("=" * 70)
        print("SENDING NEWS TO GROQ AI")
        print("=" * 70)

        print()

        print(
            "SOURCE:",
            source
        )

        print(
            "TITLE:",
            title
        )

        print(
            "KEYWORD SCORE:",
            score,
            "/ 100"
        )

        ai_result = analyze_with_ai(
            title,
            source,
            description
        )

        # ====================================================
        # DISCORD DECISION
        # ====================================================

        if ai_result:

            is_market_moving = ai_result.get(
                "is_market_moving",
                False
            )

            ai_impact = ai_result.get(
                "impact",
                "LOW"
            )

            if (
                is_market_moving
                and ai_impact in (
                    "HIGH",
                    "EXTREME"
                )
            ):

                print()
                print("=" * 70)
                print("IMPORTANT GOLD NEWS DETECTED")
                print("=" * 70)

                send_discord_alert(
                    article,
                    ai_result,
                    score,
                    matched_events
                )

            else:

                print()

                print(
                    "AI decided this news does not "
                    "require a Discord alert."
                )

    # ========================================================
    # STORE ARTICLE
    # ========================================================

    new_articles.append({

        "title":
            title,

        "url":
            link,

        "published":
            published.isoformat(),

        "source":
            source,

        "score":
            score,

        "impact":
            keyword_impact,

        "events":
            matched_events,

        "ai":
            ai_result

    })


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()

print("=" * 70)
print("NEW GOLD NEWS + AI ANALYSIS")
print("=" * 70)

print()

print(
    "New articles:",
    len(new_articles)
)


for article in new_articles:

    print()

    print("NEWS")

    print("-" * 70)

    print(
        "SOURCE:",
        article["source"]
    )

    print(
        "TITLE:",
        article["title"]
    )

    print(
        "PUBLISHED:",
        article["published"]
    )

    print(
        "KEYWORD SCORE:",
        article["score"],
        "/ 100"
    )

    print(
        "KEYWORD IMPACT:",
        article["impact"]
    )

    print(
        "MATCHED EVENTS:",
        ", ".join(
            article["events"]
        )
        if article["events"]
        else "None"
    )

    print(
        "URL:",
        article["url"]
    )

    # ========================================================
    # AI RESULT
    # ========================================================

    if article["ai"]:

        print()

        print(
            "AI ANALYSIS"
        )

        print("-" * 70)

        print(
            "Market Moving:",
            article["ai"].get(
                "is_market_moving"
            )
        )

        print(
            "Gold Direction:",
            article["ai"].get(
                "gold_direction"
            )
        )

        print(
            "AI Impact:",
            article["ai"].get(
                "impact"
            )
        )

        print(
            "AI Confidence:",
            article["ai"].get(
                "confidence"
            )
        )

        print(
            "AI Reason:",
            article["ai"].get(
                "reason"
            )
        )

        print("-" * 70)

    print("-" * 70)


# ============================================================
# UPDATE MEMORY
# ============================================================

for article in new_articles:

    seen_news.add(
        article["url"]
    )


# Keep maximum 500 URLs

if len(seen_news) > 500:

    seen_news = set(
        list(seen_news)[-500:]
    )


# ============================================================
# SAVE MEMORY
# ============================================================

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

print()

print(
    "Previously seen + new:",
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
    "High/Extreme keyword impact:",
    high_count
)

ai_count = sum(

    1

    for article in new_articles

    if article["ai"] is not None

)

print(
    "Articles analyzed by AI:",
    ai_count
)

google_count = sum(

    1

    for article in new_articles

    if article["source"] == "Google News"

)

forex_factory_count = sum(

    1

    for article in new_articles

    if article["source"] == "Forex Factory"

)

print(
    "New Google News:",
    google_count
)

print(
    "New Forex Factory:",
    forex_factory_count
)

print()

print(
    "Gold News AI Multi-Source Collector finished."
)
