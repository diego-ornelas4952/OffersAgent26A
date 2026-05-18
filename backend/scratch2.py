import asyncio
from playwright.async_api import async_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

async def human_scroll(page):
    import random
    for _ in range(3):
        await page.mouse.wheel(0, random.randint(300, 600))
        await asyncio.sleep(0.5)

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(user_agent=USER_AGENTS[0])
        page = await context.new_page()
        await page.goto("https://listado.mercadolibre.com.mx/macbook-air-m2", wait_until="domcontentloaded", timeout=45000)
        await human_scroll(page)
        
        await page.wait_for_selector(".ui-search-layout__item, .poly-card", timeout=10000)
        items = await page.query_selector_all(".ui-search-layout__item, .poly-card")
        if items:
            html = await items[0].inner_html()
            with open("item_html.txt", "w") as f:
                f.write(html)
        await browser.close()

asyncio.run(test())
