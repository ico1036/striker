# GTI657 Flight Tracker

Real-time flight tracking application for GTI657 (Atlas Air, Boeing 747-400) flying from Chicago (ORD) to Seoul (ICN).

## Features

- ✅ **Real-time Flight Data**: Extracts live flight data from FlightAware
- ✅ **Interactive Map**: Displays complete flight route on Leaflet.js map
- ✅ **Current Position**: Shows plane marker at current location
- ✅ **Flight Information**: Origin, destination, aircraft type, altitude, and coordinates
- ✅ **Auto-update**: Refreshes data every 30 seconds

## Requirements

- Python 3.12+
- `uv` package manager

## Installation

1. Install dependencies:
```bash
uv sync
uv run playwright install chromium
```

## Running the Application

Start the server:
```bash
uv run uvicorn src.main:app --reload
```

Then open your browser and navigate to:
```
http://localhost:8000
```

## How It Works

The application scrapes FlightAware's `trackpollBootstrap` JavaScript variable to extract:
- Complete flight route coordinates
- Current position (last point in track)
- Origin/destination airports
- Aircraft type and flight status

The data is displayed on an interactive Leaflet.js map showing:
- **Blue polyline**: Full flight path from Chicago to Seoul
- **Plane marker**: Current position over the Pacific Ocean
- **Info panel**: Flight details and real-time coordinates

## API Endpoint

- `GET /api/flight-data`: Returns JSON with flight information and route data

## Testing

Run the test suite:
```bash
uv run pytest tests/
```

## Project Structure

```
striker/
├── src/
│   ├── main.py          # FastAPI server
│   └── scraper.py       # FlightAware scraper
├── static/
│   └── index.html       # Frontend map interface
├── tests/
│   ├── test_main.py     # API tests
│   └── test_scraper.py  # Scraper tests
└── pyproject.toml       # Project dependencies
```

## License

MIT
# striker
