import httpx
from typing import Optional, Dict, List

class OpenSkyClient:
    """Client for OpenSky Network API"""
    
    BASE_URL = "https://opensky-network.org/api"
    
    async def get_flight_by_callsign(self, callsign: str) -> Optional[Dict]:
        """Get current state of a flight by callsign"""
        async with httpx.AsyncClient() as client:
            try:
                # Get all states and filter by callsign
                response = await client.get(f"{self.BASE_URL}/states/all")
                if response.status_code != 200:
                    return None
                
                data = response.json()
                if not data or "states" not in data:
                    return None
                
                # Find the flight with matching callsign (strip whitespace)
                for state in data["states"]:
                    if state[1] and state[1].strip().upper() == callsign.upper():
                        return self._parse_state_vector(state)
                
                return None
            except Exception as e:
                print(f"OpenSky API error: {e}")
                return None
    
    def _parse_state_vector(self, state: List) -> Dict:
        """Parse OpenSky state vector into readable format"""
        return {
            "icao24": state[0],
            "callsign": state[1].strip() if state[1] else None,
            "origin_country": state[2],
            "time_position": state[3],
            "last_contact": state[4],
            "longitude": state[5],
            "latitude": state[6],
            "baro_altitude": state[7],  # meters
            "on_ground": state[8],
            "velocity": state[9],  # m/s
            "true_track": state[10],  # degrees
            "vertical_rate": state[11],  # m/s
            "geo_altitude": state[13],  # meters
        }
