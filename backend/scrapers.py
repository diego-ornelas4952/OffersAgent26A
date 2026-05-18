import asyncio
import random
import re
from playwright.async_api import async_playwright
from typing import List, Dict, Any

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

def calculate_relevance(query: str, title: str) -> float:
    query_words = set(re.findall(r'\w+', query.lower()))
    title_words = set(re.findall(r'\w+', title.lower()))
    if not query_words: return 1.0
    matches = len(query_words.intersection(title_words))
    return matches / len(query_words)

async def human_scroll(page):
    """Simulates a human-like scroll to trigger lazy-loaded content and bypass bot detection."""
    for _ in range(3):
        await page.mouse.wheel(0, random.randint(300, 600))
        await asyncio.sleep(random.uniform(0.5, 1.2))

async def scrape_mercadolibre(browser, query: str) -> List[Dict[str, Any]]:
    context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
    page = await context.new_page()
    url = f"https://listado.mercadolibre.com.mx/{query.replace(' ', '-')}"
    products = []
    try:
        print(f"ML: Accediendo a {url}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        
        # Human behavior
        await human_scroll(page)
        
        # Super robust selector search
        selectors = [".ui-search-layout__item", ".poly-card", ".ui-search-result__wrapper", "[data-testid='search-item']"]
        found = False
        for sel in selectors:
            try:
                await page.wait_for_selector(sel, timeout=10000)
                found = True
                break
            except: continue
        
        if not found:
            print(f"ML: Bloqueo detectado o página vacía para {query}")
            # Try taking a screenshot for debugging (optional in dev)
            # await page.screenshot(path="ml_debug.png")
            return []

        items = await page.query_selector_all(".ui-search-layout__item, .poly-card, [data-testid='search-item']")
        print(f"ML: Encontrados {len(items)} items.")
        
        for item in items[:6]:
            try:
                title_elem = await item.query_selector("h2, .ui-search-item__title, .poly-component__title")
                name = await title_elem.inner_text()
                
                url_elem = await item.query_selector("a")
                href = await url_elem.get_attribute("href")
                product_url = href if href.startswith("http") else f"https://articulo.mercadolibre.com.mx{href}" if href.startswith("/") else href
                
                price_elem = await item.query_selector(".poly-price__current .andes-money-amount__fraction, .ui-search-price__second-line .andes-money-amount__fraction")
                if not price_elem:
                    price_elem = await item.query_selector(".andes-money-amount__fraction")
                if not price_elem: continue
                price = float((await price_elem.inner_text()).replace(',', ''))
                
                full_text = (await item.inner_text()).lower()
                delivery_days = 1 if any(x in full_text for x in ["mañana", "hoy", "full"]) else 3
                
                relevance = calculate_relevance(query, name)
                if relevance < 0.15: continue

                products.append({
                    "store": "Mercado Libre", "name": name.strip(), "price": price,
                    "delivery_days": delivery_days, "reputation": 4.8 if "mercado" in full_text else 4.2,
                    "cashback": 0, "url": product_url, "relevance": relevance
                })
            except: continue
    except Exception as e: print(f"ML Error: {e}")
    finally:
        await page.close()
        await context.close()
    return products

async def scrape_amazon(browser, query: str) -> List[Dict[str, Any]]:
    context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
    page = await context.new_page()
    url = f"https://www.amazon.com.mx/s?k={query.replace(' ', '+')}"
    products = []
    try:
        print(f"Amazon: Accediendo a {url}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await human_scroll(page)
        
        if "captcha" in (await page.title()).lower():
            print("Amazon: CAPTCHA detectado.")
            return []

        try:
            await page.wait_for_selector(".s-result-item[data-component-type='s-search-result']", timeout=10000)
        except:
            print(f"Amazon: No se encontraron resultados o bloqueo para {query}")
            return []

        items = await page.query_selector_all(".s-result-item[data-component-type='s-search-result']")
        for item in items[:6]:
            try:
                name_elem = await item.query_selector("h2 span, h2")
                name = await name_elem.inner_text()
                
                url_elem = await item.query_selector("[data-cy='title-recipe'] a, h2 a, a:has(h2)")
                if not url_elem: continue
                href = await url_elem.get_attribute("href")
                
                # Intentar limpiar la URL (evita que adblockers como Brave bloqueen el link)
                asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                if asin_match:
                    product_url = f"https://www.amazon.com.mx/dp/{asin_match.group(1)}"
                else:
                    product_url = "https://www.amazon.com.mx" + href if href.startswith("/") else href
                
                price_elem = await item.query_selector(".a-price-whole")
                if not price_elem: continue
                price = float((await price_elem.inner_text()).replace(',', '').replace('.', '').strip())
                
                full_text = (await item.inner_text()).lower()
                delivery_days = 1 if any(x in full_text for x in ["mañana", "hoy"]) else 2
                
                relevance = calculate_relevance(query, name)
                if relevance < 0.15: continue

                products.append({
                    "store": "Amazon", "name": name.strip(), "price": price,
                    "delivery_days": delivery_days, "reputation": 4.5,
                    "cashback": 0, "url": product_url, "relevance": relevance
                })
            except: continue
    except Exception as e: print(f"Amazon Error: {e}")
    finally:
        await page.close()
        await context.close()
    return products

async def scrape_all(query: str) -> List[Dict[str, Any]]:
    async with async_playwright() as p:
        # We launch with a bit of "noise" to be less detectable
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        tasks = [scrape_mercadolibre(browser, query), scrape_amazon(browser, query)]
        results = await asyncio.gather(*tasks)
        await browser.close()
        
        ml_products = results[0] if results[0] else []
        amazon_products = results[1] if results[1] else []
        
        final_products = []
        ml_count = len(ml_products)
        amazon_count = len(amazon_products)
        
        if ml_count >= 2 and amazon_count >= 2:
            final_products.extend(ml_products[:2])
            final_products.extend(amazon_products[:2])
        elif ml_count < 2:
            final_products.extend(ml_products)
            needed = 4 - len(final_products)
            final_products.extend(amazon_products[:needed])
        elif amazon_count < 2:
            final_products.extend(amazon_products)
            needed = 4 - len(final_products)
            final_products.extend(ml_products[:needed])
            
        return final_products
