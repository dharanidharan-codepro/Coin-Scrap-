"""
Cryptocurrency market data retrieval from the CoinGecko API.
"""

import logging

import requests


logger = logging.getLogger(__name__)


class CryptoScraper:
    """Fetch cryptocurrency market data without launching a browser."""

    API_URL = "https://api.coingecko.com/api/v3/coins/markets"
    PAGE_SIZE = 250
    MAX_RESULTS = 2000

    def scrape_top_crypto(self, limit=10):
        """Return market data for the requested number of cryptocurrencies."""
        target = None if isinstance(limit, str) and limit.lower() == "all" else max(1, int(limit))
        if target is not None:
            target = min(target, self.MAX_RESULTS)

        cryptos = []
        page = 1
        while target is None or len(cryptos) < target:
            page_size = self.PAGE_SIZE if target is None else min(self.PAGE_SIZE, target - len(cryptos))
            response = requests.get(
                self.API_URL,
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": page_size,
                    "page": page,
                    "sparkline": "false",
                },
                timeout=10,
            )
            response.raise_for_status()
            items = response.json()
            if not items:
                break

            for item in items:
                market_cap = item.get("market_cap")
                price = item.get("current_price")
                change = item.get("price_change_percentage_24h")
                cryptos.append({
                    "rank": len(cryptos) + 1,
                    "name": item.get("name"),
                    "symbol": (item.get("symbol") or "").upper(),
                    "image_url": item.get("image"),
                    "price": f"${price:,}" if price is not None else "N/A",
                    "change_24h": f"{change:.2f}%" if change is not None else "N/A",
                    "market_cap": f"${int(market_cap):,}" if market_cap is not None else "N/A",
                })

            if target is not None and len(cryptos) >= target:
                break
            page += 1
            if len(cryptos) >= self.MAX_RESULTS:
                logger.warning("Reached safety cap when fetching from CoinGecko")
                break

        logger.info("Successfully retrieved %s cryptocurrencies via CoinGecko", len(cryptos))
        return cryptos
