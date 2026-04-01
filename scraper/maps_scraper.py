import asyncio
import csv
import os
from datetime import datetime
from playwright.async_api import async_playwright

# ── CONFIG ──────────────────────────────────────────────
SEARCH_QUERY = "cleaning services"
LOCATION     = "New York, NY"
MAX_RESULTS  = 30
OUTPUT_DIR   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
# ────────────────────────────────────────────────────────


async def scrape_google_maps(query: str, location: str, max_results: int = 10):
    search_term = f"{query} in {location}"
    results     = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page    = await browser.new_page()

        print(f"[+] Searching: {search_term}")
        await page.goto(
            f"https://www.google.com/maps/search/{search_term.replace(' ', '+')}",
            wait_until="domcontentloaded",
            timeout=60000
        )
        await page.wait_for_timeout(4000)

        # ── Scroll to load more listings ──
        print("[+] Scrolling to load listings...")
        for _ in range(10):
            try:
                feed = page.locator('div[role="feed"]')
                await feed.evaluate("el => el.scrollBy(0, 2000)")
                await page.wait_for_timeout(2000)

                # Check if we have enough links already
                current_links = await page.eval_on_selector_all(
                    'a[href*="/maps/place/"]',
                    "els => els.map(e => e.href)"
                )
                if len(current_links) >= max_results:
                    break
            except:
                break

        # ── Collect all place URLs after scrolling ──
        print("[+] Collecting place URLs...")
        all_links = await page.eval_on_selector_all(
            'a[href*="/maps/place/"]',
            "els => els.map(e => e.href)"
        )

        # Deduplicate URLs
        seen  = set()
        hrefs = []
        for link in all_links:
            base = link.split("/@")[0]  # strip coordinates
            if base not in seen and "/maps/place/" in base:
                seen.add(base)
                hrefs.append(link)

        hrefs = hrefs[:max_results]
        print(f"[+] Found {len(hrefs)} unique place URLs. Visiting each...")

        # ── Visit each place URL directly ──
        for i, href in enumerate(hrefs):
            try:
                await page.goto(href, wait_until="domcontentloaded", timeout=30000)

                # Wait for place name to load
                try:
                    await page.wait_for_selector('h1', timeout=5000)
                    await page.wait_for_timeout(1000)
                except:
                    await page.wait_for_timeout(2000)

                # ── Extract fields ──────────────────────
                name = await get_text(page, 'h1.fontHeadlineLarge')
                if not name:
                    name = await get_text(page, 'h1')

                rating = await get_text(page, 'span.fontDisplayLarge')
                if not rating:
                    rating = await get_text(page, 'div.fontDisplayLarge')

                reviews = await get_attr(page, 'span[aria-label*="review"]', "aria-label")
                if reviews:
                    reviews = reviews.replace(",", "").split(" ")[0]

                category = await get_text(page, 'button[jsaction*="category"]')
                address  = await get_text(page, 'button[data-item-id="address"] div[class*="fontBodyMedium"]')
                phone    = await get_text(page, 'button[data-item-id*="phone"] div[class*="fontBodyMedium"]')
                website  = await get_attr(page, 'a[data-item-id="authority"]', "href")

                business = {
                    "name":       name     or "N/A",
                    "category":   category or "N/A",
                    "address":    address  or "N/A",
                    "phone":      phone    or "N/A",
                    "website":    website  or "N/A",
                    "rating":     rating   or "N/A",
                    "reviews":    reviews  or "N/A",
                    "location":   location,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }

                results.append(business)
                print(f"  [{i+1}] {business['name']} | {business['rating']} stars | {business['address']}")

            except Exception as e:
                print(f"  [!] Error on listing {i+1}: {e}")
                continue

        await browser.close()

    return results


async def get_text(page, selector, attr=None):
    try:
        el = page.locator(selector).first
        if attr:
            return await el.get_attribute(attr, timeout=2000)
        return (await el.inner_text(timeout=2000)).strip()
    except:
        return None


async def get_attr(page, selector, attr):
    try:
        el = page.locator(selector).first
        return await el.get_attribute(attr, timeout=2000)
    except:
        return None


def save_to_csv(data: list, query: str, location: str):
    if not data:
        print("[!] No data to save.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{OUTPUT_DIR}/{query.replace(' ', '_')}_{location.replace(', ', '_')}_{timestamp}.csv"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"\n[✓] Saved {len(data)} businesses to: {filename}")
    return filename


async def main():
    data = await scrape_google_maps(SEARCH_QUERY, LOCATION, MAX_RESULTS)
    save_to_csv(data, SEARCH_QUERY, LOCATION)


if __name__ == "__main__":
    asyncio.run(main())