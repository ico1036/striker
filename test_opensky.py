import asyncio
from src.opensky_client import OpenSkyClient

async def main():
    client = OpenSkyClient()
    result = await client.get_flight_by_callsign("GTI657")
    print(f"Result for GTI657: {result}")
    
    # Also try some other GTI flights to see if any are in the air
    result2 = await client.get_flight_by_callsign("GTI8517")
    print(f"Result for GTI8517: {result2}")

if __name__ == "__main__":
    asyncio.run(main())
