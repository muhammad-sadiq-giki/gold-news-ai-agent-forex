# 🥇 Gold News AI Agent & Forex Alert System

An automated AI-powered gold news monitoring system that collects breaking financial and geopolitical news, evaluates its potential impact on gold prices, and sends important alerts to Discord.

The system is designed to monitor events that may influence **Gold / XAUUSD**, including:

- Federal Reserve decisions
- Interest rates
- Inflation
- US dollar movements
- Tariffs and trade wars
- Iran and Middle East conflicts
- Geopolitical tensions
- Military attacks
- Sanctions
- Major economic developments

---

## 🚀 How It Works

The system runs automatically using GitHub Actions.

```text
                 Google News RSS
                       │
                       ▼
             rss_gold_collector.py
                       │
                       ▼
                News Collection
                       │
                       ▼
                 Keyword Filter
                       │
                       ▼
                 Impact Scoring
                       │
                       ▼
                   Groq AI
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       Important News       Not Important
             │                   │
             ▼                   ▼
       Discord Alert            Ignore
             │
             ▼
        seen_news.json
