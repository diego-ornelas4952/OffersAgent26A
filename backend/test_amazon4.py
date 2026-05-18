import asyncio
from playwright.async_api import async_playwright

USER_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"]

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(user_agent=USER_AGENTS[0])
        page = await context.new_page()
        await page.goto("https://www.amazon.com.mx/s?k=macbook+air+m2", wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_selector(".s-result-item[data-component-type='s-search-result']", timeout=10000)
        items = await page.query_selector_all(".s-result-item[data-component-type='s-search-result']")
        if items:
            html = await items[0].inner_html()
            with open("amazon_item.html", "w") as f:
                f.write(html)
        await browser.close()

asyncio.run(test())
