from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.scraper import FlightScraper
from src.drone import DroneInterceptor
from pydantic import BaseModel

app = FastAPI()
drone = DroneInterceptor()

# Data models
class TargetUpdate(BaseModel):
    lat: float
    lon: float
    alt: float

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/api/flight-data")
async def get_flight_data():
    scraper = FlightScraper("EVA170")
    data = await scraper.get_flight_data()
    return data

@app.post("/api/drone/launch")
async def launch_drone():
    drone.launch()
    return {"status": "launched", "message": "Drone launched from Incheon Airport"}

@app.post("/api/drone/update")
async def update_drone(target: TargetUpdate):
    state = drone.update(target.lat, target.lon, target.alt)
    return state
