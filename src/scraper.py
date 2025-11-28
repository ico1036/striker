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
                
                # Extract trackpollBootstrap data and current speed/altitude from page
                track_data = await page.evaluate("""
                    () => {
                        const result = {
                            trackpoll: window.trackpollBootstrap || null,
                            currentData: {}
                        };
                        
                        // Extract current speed and altitude using regex from page text
                        const bodyText = document.body.innerText;
                        
                        // Find all speed values (prioritize first occurrence which is usually current)
                        const speedKmhMatches = bodyText.match(/(\\d+)\\s*km\\/h/g);
                        const speedKtsMatches = bodyText.match(/(\\d+)\\s*(kts|knots)/g);
                        
                        if (speedKmhMatches && speedKmhMatches.length > 0) {
                            const match = speedKmhMatches[0].match(/(\\d+)/);
                            if (match) result.currentData.speed_kmh = parseInt(match[1]);
                        }
                        if (speedKtsMatches && speedKtsMatches.length > 0) {
                            const match = speedKtsMatches[0].match(/(\\d+)/);
                            if (match) result.currentData.speed_kts = parseInt(match[1]);
                        }
                        
                        // Find altitude values
                        const altMetersMatches = bodyText.match(/([\\d,]+)\\s*m(?![a-z])/g);
                        const altFeetMatches = bodyText.match(/([\\d,]+)\\s*ft/g);
                        
                        if (altMetersMatches && altMetersMatches.length > 0) {
                            // Look for values > 1000 (likely altitude, not distance)
                            for (const match of altMetersMatches) {
                                const numMatch = match.match(/([\\d,]+)/);
                                if (numMatch) {
                                    const altStr = numMatch[1].replace(/,/g, '');
                                    const altVal = parseInt(altStr);
                                    if (altVal > 1000) {
                                        result.currentData.altitude_meters = altVal;
                                        break;
                                    }
                                }
                            }
                        }
                        if (altFeetMatches && altFeetMatches.length > 0) {
                            for (const match of altFeetMatches) {
                                const numMatch = match.match(/([\\d,]+)/);
                                if (numMatch) {
                                    const altStr = numMatch[1].replace(/,/g, '');
                                    const altVal = parseInt(altStr);
                                    if (altVal > 5000) {
                                        result.currentData.altitude_feet = altVal;
                                        break;
                                    }
                                }
                            }
                        }
                        
                        return result;
                    }
                """)
                
                if not track_data or not track_data.get("trackpoll"):
                    await browser.close()
                    return {"flight_id": self.flight_id, "error": "No track data found"}
                
                # Extract the trackpoll and current data
                current_page_data = track_data.get("currentData", {})
                track_data = track_data.get("trackpoll")
                
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
                    # Track items are objects with 'coord', 'alt', 'gs' (ground speed), 'heading', etc.
                    last_track = track[-1]
                    if isinstance(last_track, dict):
                        # Start with track data
                        current_pos = {
                            "coord": last_track.get("coord", []),
                            "alt": last_track.get("alt"),
                            "gs": last_track.get("gs"),  # ground speed in knots
                            "heading": last_track.get("heading"),
                            "timestamp": last_track.get("timestamp")
                        }
                        
                        # Override with page data if available (more current)
                        if current_page_data.get("altitude_feet"):
                            current_pos["alt"] = current_page_data["altitude_feet"]
                        elif current_page_data.get("altitude_meters"):
                            current_pos["alt"] = int(current_page_data["altitude_meters"] * 3.28084)
                        
                        if current_page_data.get("speed_kts"):
                            current_pos["gs"] = current_page_data["speed_kts"]
                        elif current_page_data.get("speed_kmh"):
                            current_pos["gs"] = int(current_page_data["speed_kmh"] / 1.852)
                        
                        # If still no speed/alt, find last valid track point
                        if not current_pos.get("alt") or not current_pos.get("gs"):
                            for i in range(len(track) - 1, max(0, len(track) - 100), -1):
                                point = track[i]
                                if isinstance(point, dict):
                                    if not current_pos.get("alt") and point.get("alt"):
                                        current_pos["alt"] = point["alt"]
                                    if not current_pos.get("gs") and point.get("gs"):
                                        current_pos["gs"] = point["gs"]
                                    if current_pos.get("alt") and current_pos.get("gs"):
                                        break
                
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
                        "ground_speed_knots": current_pos["gs"] if current_pos else None,
                        "ground_speed_kmh": int(current_pos["gs"] * 1.852) if current_pos and current_pos["gs"] else None,
                        "heading": current_pos["heading"] if current_pos else None,
                        "timestamp": current_pos["timestamp"] if current_pos else None,
                    },
                    "route": [[item["coord"][0], item["coord"][1]] for item in track if isinstance(item, dict) and "coord" in item and len(item["coord"]) >= 2],
                    "raw_track_data": track
                }
                
                await browser.close()
                return result
                
            except Exception as e:
                await browser.close()
                return {"flight_id": self.flight_id, "error": str(e)}

