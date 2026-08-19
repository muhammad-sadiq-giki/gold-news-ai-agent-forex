HOT_EVENTS = {

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

    "$100": 50,
    "$50": 30,

    "record high": 45,
    "all-time high": 50,

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

    "tariff": 25,
    "tariffs": 25,

    "trade war": 45,
    "trade deal": 25,

    "banking crisis": 60,
    "bank failure": 60,
    "bank collapse": 70,

    "financial crisis": 60,
    "market crash": 60,

    "us dollar": 20,
    "dollar falls": 30,
    "dollar drops": 35,
    "dollar plunges": 50,

    "dollar rises": 20,
    "dollar strengthens": 25,

    "central bank": 20,
    "central banks": 20,

    "ecb": 20,
    "boj": 20,
    "bank of japan": 25,
    "bank of england": 20,

    "trump": 10
}


def calculate_score(title):

    title_lower = title.lower()

    score = 0
    matched_events = []

    for event, points in HOT_EVENTS.items():

        if event in title_lower:

            score += points
            matched_events.append(event)

    score = min(score, 100)

    if score >= 80:
        impact = "EXTREME"

    elif score >= 60:
        impact = "HIGH"

    elif score >= 30:
        impact = "MEDIUM"

    else:
        impact = "LOW"

    return score, impact, matched_events


# ============================================================
# TEST ARTICLES
# ============================================================

test_titles = [

    "Gold Leaps $100 on US Treasury Bond Buybacks News",

    "Federal Reserve unexpectedly cuts interest rates",

    "Major missile strike reported in the Middle East",

    "Gold prices remain steady",

    "US inflation rises more than expected",

    "Trump announces new tariffs",

]


print("=" * 70)
print("GOLD IMPACT SCORE TEST")
print("=" * 70)


for title in test_titles:

    score, impact, events = calculate_score(title)

    print()
    print("TITLE:")
    print(title)

    print()
    print("SCORE:", score, "/ 100")
    print("IMPACT:", impact)

    print("MATCHED EVENTS:")

    if events:
        print(", ".join(events))
    else:
        print("None")

    print("-" * 70)
