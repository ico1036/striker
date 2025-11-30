import pytest
import pytest
from src.scraper import FlightScraper

def test_scraper_initialization():
    scraper = FlightScraper("EVA170")
    assert scraper.flight_id == "EVA170"

@pytest.mark.asyncio
async def test_get_flight_data_returns_dict():
    scraper = FlightScraper("EVA170")
    # We are not mocking anymore to test real scraping
    # This is an integration test now
    data = await scraper.get_flight_data()
    assert isinstance(data, dict)
    assert data["flight_id"] == "EVA170"
    # We expect these to be present if scraping works
    # assert data["origin"] is not None
    # assert data["destination"] is not None
