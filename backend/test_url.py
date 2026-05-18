import asyncio
from playwright.async_api import async_playwright
from scrapers import scrape_amazon

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        products = await scrape_amazon(browser, "macbook air m2")
        for p in products:
            print("URL:", repr(p['url']))
        await browser.close()

asyncio.run(test())
