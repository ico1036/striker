import asyncio
from playwright.async_api import async_playwright
import json
import re

async def extract_flight_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to FlightAware...")
        await page.goto("https://www.flightaware.com/live/flight/GTI657", timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(10000)  # Wait for JS to load
        
        print("Extracting data...")
        
        # Try to extract trackpollBootstrap or similar variables
        result = await page.evaluate("""
            () => {
                // Look for all window variables
                const data = {};
                
                // Common FlightAware variables
                if (window.trackpollBootstrap) data.trackpollBootstrap = window.trackpollBootstrap;
                if (window.trackpollGlobals) data.trackpollGlobals = window.trackpollGlobals;
                if (window.flightPageData) data.flightPageData = window.flightPageData;
                
                // Search for any variable with track/flight/map in name
                for (let key in window) {
                    if (typeof window[key] === 'object' && window[key] !== null) {
                        const keyLower = key.toLowerCase();
                        if (keyLower.includes('track') || keyLower.includes('flight') || keyLower.includes('map')) {
                            try {
                                const str = JSON.stringify(window[key]);
                                if (str.includes('lat') || str.includes('lon') || str.includes('coord')) {
                                    data[key] = window[key];
                                }
                            } catch(e) {}
                        }
                    }
                }
                
                return data;
            }
        """)
        
        print("Found data:")
        print(json.dumps(result, indent=2))
        
        # Save to file for inspection
        with open("flightaware_extracted.json", "w") as f:
            json.dump(result, f, indent=2)
        
        await browser.close()
        return result

if __name__ == "__main__":
    asyncio.run(extract_flight_data())
