from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.scraper import FlightScraper

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/api/flight-data")
async def get_flight_data():
    scraper = FlightScraper("GTI657")
    data = await scraper.get_flight_data()
    return data
