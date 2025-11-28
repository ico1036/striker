import asyncio
from src.scraper import FlightScraper
import json

async def main():
    scraper = FlightScraper("GTI657")
    data = await scraper.get_flight_data()
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
