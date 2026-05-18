import asyncio
from playwright.async_api import async_playwright
import re

USER_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"]

def calculate_relevance(query: str, title: str) -> float:
    query_words = set(re.findall(r'\w+', query.lower()))
    title_words = set(re.findall(r'\w+', title.lower()))
    if not query_words: return 1.0
    matches = len(query_words.intersection(title_words))
    return matches / len(query_words)

async def test(query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(user_agent=USER_AGENTS[0])
        page = await context.new_page()
        url = f"https://www.amazon.com.mx/s?k={query.replace(' ', '+')}"
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_selector(".s-result-item[data-component-type='s-search-result']", timeout=10000)
        items = await page.query_selector_all(".s-result-item[data-component-type='s-search-result']")
        print(f"Items found: {len(items)}")
        
        products = []
        for item in items[:6]:
            try:
                name_elem = await item.query_selector("h2 a span")
                if not name_elem:
                    print("no name_elem")
                    continue
                name = await name_elem.inner_text()
                
                url_elem = await item.query_selector("h2 a")
                href = await url_elem.get_attribute("href")
                
                price_elem = await item.query_selector(".a-price-whole")
                if not price_elem:
                    print("no price elem for", name)
                    continue
                price_str = await price_elem.inner_text()
                price = float(price_str.replace(',', '').replace('.', '').strip())
                
                relevance = calculate_relevance(query, name)
                if relevance < 0.15:
                    print("relevance too low:", relevance, name)
                    continue
                
                print(f"OK: {name[:30]}... ${price}")
                products.append(name)
            except Exception as e:
                print("Exception on item:", e)
        print("Total extracted:", len(products))
        await browser.close()

asyncio.run(test("macbook air m2"))
