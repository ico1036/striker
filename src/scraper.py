from playwright.async_api import async_playwright

class FlightScraper:
    def __init__(self, flight_id: str):
        self.flight_id = flight_id
        self.base_url = f"https://www.flightaware.com/live/flight/{flight_id}"

    async def get_flight_data(self) -> dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.base_url, timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_timeout(10000)  # Wait for JS to execute
                
                # Extract trackpollBootstrap data
                track_data = await page.evaluate("""
                    () => {
                        if (window.trackpollBootstrap) {
                            return window.trackpollBootstrap;
                        }
                        return null;
                    }
                """)
                
                if not track_data:
                    await browser.close()
                    return {"flight_id": self.flight_id, "error": "No track data found"}
                
                # Parse the track data
                flights = track_data.get("flights", {})
                
                # FlightAware uses keys like "GTI657-1764256174-sw-362p:0"
                # Find the key that starts with our flight_id
                flight_key = None
                for key in flights.keys():
                    if key.startswith(self.flight_id):
                        flight_key = key
                        break
                
                if not flight_key:
                    await browser.close()
                    return {"flight_id": self.flight_id, "error": f"Flight {self.flight_id} not found in track data"}
                
                flight_info = flights[flight_key]
                
                # Get track data from the top level of flight_info
                track = flight_info.get("track", [])
                
                # Also get activity log for origin/dest/aircraft info
                activity_log = flight_info.get("activityLog", {})
                flights_list = activity_log.get("flights", [])
                
                # Get current flight info (first in list)
                current_flight = flights_list[0] if flights_list else {}
                
                # Get current position (last point in track)
                current_pos = None
                if track:
                    # Track items are objects with 'coord', 'alt', etc.
                    last_track = track[-1]
                    if isinstance(last_track, dict):
                        current_pos = {
                            "coord": last_track.get("coord", []),
                            "alt": last_track.get("alt")
                        }
                
                # Extract origin and destination from current flight or flight_info
                origin = current_flight.get("origin") or flight_info.get("origin", {})
                destination = current_flight.get("destination") or flight_info.get("destination", {})
                aircraft = current_flight.get("aircraft") or flight_info.get("aircraft", {})
                
                result = {
                    "flight_id": self.flight_id,
                    "origin": origin.get("iata") or origin.get("icao") if origin else None,
                    "destination": destination.get("iata") or destination.get("icao") if destination else None,
                    "aircraft_type": aircraft.get("type") if aircraft else None,
                    "current_position": {
                        "longitude": current_pos["coord"][0] if current_pos and len(current_pos["coord"]) >= 2 else None,
                        "latitude": current_pos["coord"][1] if current_pos and len(current_pos["coord"]) >= 2 else None,
                        "altitude_feet": current_pos["alt"] if current_pos else None,
                        "altitude_meters": int(current_pos["alt"] * 0.3048) if current_pos and current_pos["alt"] else None,
                    },
                    "route": [[item["coord"][0], item["coord"][1]] for item in track if isinstance(item, dict) and "coord" in item and len(item["coord"]) >= 2],
                    "raw_track_data": track
                }
                
                await browser.close()
                return result
                
            except Exception as e:
                await browser.close()
                return {"flight_id": self.flight_id, "error": str(e)}

