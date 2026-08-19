import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import json
import os


# ============================================================
# CONFIGURATION
# ============================================================

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

MAX_AGE_HOURS = 2

HEADERS = {
    "User-Agent": "Mozilla/5.0 GoldNewsAI/1.0"
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
    "gold plunges": 70,
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

    # TREASURY / BONDS
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

    # FED
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

    # ECONOMIC DATA
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

    # GEOPOLITICAL
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

    # US DOLLAR
    "us dollar": 20,
    "dollar falls": 30,
    "dollar drops": 35,
    "dollar plunges": 50,
    "dollar rises": 20,
    "dollar strengthens": 25,

    # CENTRAL BANKS
    "central bank": 20,
    "central banks": 20,
    "ecb": 20,
    "boj": 20,
    "bank of japan": 25,
    "bank of england": 20,

    # POLITICS
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
print("GOLD NEWS AI COLLECTOR")
print("=" * 70)

print()

print(
    "Previously seen articles:",
    len(seen_news)
)


# ============================================================
# DOWNLOAD RSS
# ============================================================

try:

    response = requests.get(
        RSS_URL,
        headers=HEADERS,
        timeout=30
    )

    print(
        "HTTP status:",
        response.status_code
    )

    response.raise_for_status()

except requests.RequestException as error:

    print()
    print("RSS request failed:")
    print(error)

    exit(1)


# ============================================================
# PARSE RSS
# ============================================================

try:

    root = ET.fromstring(
        response.content
    )

except ET.ParseError as error:

    print()
    print("Could not parse RSS:")
    print(error)

    exit(1)


items = root.findall(".//item")


print(
    "Total RSS articles:",
    len(items)
)


# ============================================================
# TIME FILTER
# ============================================================

now = datetime.now(
    timezone.utc
)

cutoff_time = now - timedelta(
    hours=MAX_AGE_HOURS
)


# ============================================================
# DISCORD FUNCTION
# ============================================================

def send_discord_alert(
    article,
    ai_result
):

    if not DISCORD_WEBHOOK:

        print()
        print(
            "ERROR: DISCORD_WEBHOOK is missing."
        )

        return False


    title = article["title"]

    url = article["url"]

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
        f"**News:** {title}\n\n"
        f"**Gold Direction:** {direction}\n"
        f"**AI Impact:** {impact}\n"
        f"**Confidence:** {confidence}%\n\n"
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

def analyze_with_ai(title):

    if not GROQ_API_KEY:

        print()
        print(
            "ERROR: GROQ_API_KEY is missing."
        )

        return None


    prompt = f"""
You are a professional financial news analyst specializing in Gold (XAU/USD).

Analyze this news headline:

{title}

Determine whether this news could cause a sudden meaningful movement
in Gold/XAUUSD.

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


    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    if not title or not link or not pub_date:

        continue


    # --------------------------------------------------------
    # Publication date
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
    # Recent news only
    # --------------------------------------------------------

    if published < cutoff_time:

        continue


    # --------------------------------------------------------
    # Previously seen?
    # --------------------------------------------------------

    if link in seen_news:

        continue


    # --------------------------------------------------------
    # Duplicate during this run?
    # --------------------------------------------------------

    if link in new_urls:

        continue


    new_urls.add(link)


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


    score = min(
        score,
        100
    )


    # ========================================================
    # KEYWORD IMPACT
    # ========================================================

    if score >= 80:

        impact = "EXTREME"

    elif score >= 60:

        impact = "HIGH"

    elif score >= 30:

        impact = "MEDIUM"

    else:

        impact = "LOW"


    # ========================================================
    # AI ANALYSIS
    # ========================================================

    ai_result = None


    # Only important keyword candidates go to AI

    if score >= 30:

        print()
        print("=" * 70)
        print("SENDING NEWS TO GROQ AI")
        print("=" * 70)

        print()
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
            title
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
                    {
                        "title": title,
                        "url": link
                    },
                    ai_result
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

        "score":
            score,

        "impact":
            impact,

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


print()
print(
    "Gold News AI Collector finished."
)
