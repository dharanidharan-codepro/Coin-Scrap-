# CryptoTracker

CryptoTracker is a lightweight cryptocurrency market dashboard that scrapes live market data from CoinGecko, stores it in CSV files, and serves a responsive frontend with market summaries, gainers/losers, and search features.

## Features

- Live cryptocurrency market data from CoinGecko
- Top gainers and losers analysis
- Market summary statistics
- Search by coin name or symbol
- CSV export and historical data retention
- Frontend dashboard served by the Flask backend

## Project Structure

```text
Coin_Scrap -proj/
├── backend/
│   ├── app.py
│   ├── analytics.py
│   ├── processor.py
│   ├── scraper.py
│   ├── storage.py
│   ├── requirements.txt
│   ├── test_health.py
│   └── test_scrape.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── data/
│   └── crypto_data.csv
└── README.md
```

## Tech Stack

- Python
- Flask
- Pandas
- Requests
- JavaScript / HTML / CSS

## Prerequisites

- Python 3.9+
- pip

## Setup

1. Open a terminal in the project root.
2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install the backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Run the Application

Start the Flask backend:

```bash
cd backend
python app.py
```

The app will run on:

```text
http://127.0.0.1:5000
```

The frontend is served directly by the backend, so opening the browser to the local server will load the dashboard automatically.

## API Endpoints

The backend exposes these main routes:

- `GET /api/health` — health check
- `POST /api/scrape` — scrape the latest crypto data
- `GET /api/data` — fetch stored data
- `GET /api/analytics/gainers` — top gainers
- `GET /api/analytics/losers` — top losers
- `GET /api/analytics/summary` — market summary
- `GET /api/search?q=<query>` — search cryptocurrencies
- `GET /api/export` — export the latest data as CSV
- `GET /api/files` — list stored CSV files

## Example Request

```bash
curl -X POST http://127.0.0.1:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

## Data Storage

The app stores scraped market data in the `data/` directory as CSV files. Historical entries are appended over time, and the latest record for each coin is used for analytics and display.

## Notes

- The app fetches cryptocurrency data from CoinGecko.
- Network access is required for live scraping.
- The dashboard is designed for local use and project experimentation.

## License

This project is provided for educational and development use.
