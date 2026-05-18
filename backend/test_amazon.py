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

async def scrape_amazon_test(query: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(user_agent=USER_AGENTS[0])
        page = await context.new_page()
        url = f"https://www.amazon.com.mx/s?k={query.replace(' ', '+')}"
        try:
            print(f"Amazon: Accediendo a {url}...")
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await human_scroll(page)
            
            title = await page.title()
            print("Title:", title)
            
            if "captcha" in title.lower():
                print("Amazon: CAPTCHA detectado.")
                html = await page.content()
                with open("amazon_captcha.html", "w") as f:
                    f.write(html)
                return []
            
            await page.wait_for_selector(".s-result-item[data-component-type='s-search-result']", timeout=10000)
            items = await page.query_selector_all(".s-result-item[data-component-type='s-search-result']")
            print(f"Items found: {len(items)}")
            
            for item in items[:2]:
                html = await item.inner_html()
                print("--- ITEM HTML ---")
                print(html[:200] + "...")
                price_elem = await item.query_selector(".a-price-whole")
                print("Price elem:", price_elem)
                
        except Exception as e:
            print("Exception:", e)
        finally:
            await browser.close()

asyncio.run(scrape_amazon_test("macbook air m2"))
