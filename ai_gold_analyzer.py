import os
import json
import requests


GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY is not configured.")
    exit(1)


def analyze_gold_news(title):

    prompt = f"""
You are a professional financial news analyst specializing in Gold (XAU/USD).

Analyze the following breaking-news headline.

HEADLINE:
{title}

Your task is to determine whether this news could cause a sudden,
meaningful movement in Gold/XAUUSD.

IMPORTANT:
- Do NOT give trading advice.
- Do NOT predict an exact price.
- Focus only on likely market impact.
- Ignore ordinary commentary and old/background information.
- Pay special attention to unexpected Fed decisions, interest rates,
  inflation, US dollar moves, Treasury yields, major geopolitical events,
  wars, military attacks, sanctions, and major economic surprises.

Return ONLY valid JSON in this exact format:

{{
  "is_market_moving": true,
  "gold_direction": "BULLISH",
  "impact": "EXTREME",
  "confidence": 90,
  "reason": "Short explanation"
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
"""


    url = "https://api.groq.com/openai/v1/chat/completions"


    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }


    data = {
        "model": "llama-3.1-8b-instant",
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
        url,
        headers=headers,
        json=data,
        timeout=30
    )


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
