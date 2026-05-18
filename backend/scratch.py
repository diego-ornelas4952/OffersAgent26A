import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://listado.mercadolibre.com.mx/macbook-air-m2")
        await page.wait_for_selector(".ui-search-layout__item, .poly-card", timeout=10000)
        items = await page.query_selector_all(".ui-search-layout__item, .poly-card")
        for item in items[:2]:
            title_elem = await item.query_selector("h2, .ui-search-item__title, .poly-component__title")
            name = await title_elem.inner_text() if title_elem else "N/A"
            
            prices = await item.query_selector_all(".andes-money-amount__fraction")
            price_texts = []
            for p_elem in prices:
                price_texts.append(await p_elem.inner_text())
                
            print(f"Name: {name}, Prices: {price_texts}")
        await browser.close()

asyncio.run(test())
