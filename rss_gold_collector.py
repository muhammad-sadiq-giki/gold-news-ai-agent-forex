name: RSS Gold Collector

on:
  workflow_dispatch:

jobs:
  collect-gold-news:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install requests
        run: pip install requests

      - name: Collect recent gold news
        run: python rss_gold_collector.py
