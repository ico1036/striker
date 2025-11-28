import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://ko.flightaware.com/live/flight/GTI657")
        
        # Wait for some content to load
        await page.wait_for_timeout(5000)
        
        content = await page.content()
        for line in content.splitlines():
            if "trackpoll" in line:
                print(f"Found trackpoll: {line[:500]}...") # Print first 500 chars
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
