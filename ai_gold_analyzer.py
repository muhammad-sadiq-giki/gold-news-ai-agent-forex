import os
import json
import requests


GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY is not configured.")
    exit(1)


API_URL = "https://api.groq.com/openai/v1/chat/completions"

MODEL = "llama-3.1-8b-instant"


def analyze_gold_news(title):

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
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }


    payload = {
        "model": MODEL,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": 0,

        "response_format": {
            "type": "json_object"
        }
    }


    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=60
    )


    # Show useful error information
    if response.status_code != 200:

        print("Groq HTTP status:", response.status_code)
        print("Groq response:", response.text)

        response.raise_for_status()


    result = response.json()

    content = result["choices"][0]["message"]["content"]

    return json.loads(content)


# ============================================================
# TEST
# ============================================================

test_headlines = [

    "Gold Leaps $100 on US Treasury Bond Buybacks News",

    "Federal Reserve unexpectedly cuts interest rates",

    "Major missile strike reported in the Middle East",

    "Gold prices remain steady"

]


print("=" * 70)
print("AI GOLD NEWS ANALYZER")
print("=" * 70)


for title in test_headlines:

    print()
    print("HEADLINE:")
    print(title)

    try:

        result = analyze_gold_news(title)

        print()
        print(json.dumps(
            result,
            indent=2
        ))

    except Exception as error:

        print()
        print("AI ANALYSIS FAILED:")
        print(error)

    print("-" * 70)
