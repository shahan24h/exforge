import os
import sys
import csv
import time
import random
import googlemaps
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import init_db, insert_lead


# ── CONFIG ──────────────────────────────────────────────
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OUTPUT_DIR          = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)
# ────────────────────────────────────────────────────────


def scrape_google_maps(query: str, location: str, max_results: int = 30) -> list:
    """
    Fetch businesses from Google Maps using the official Places API.
    Returns a list of business dicts.
    """
    gmaps       = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    search_term = f"{query} in {location}"
    results     = []
    seen_ids    = set()

    print(f"[+] Searching: {search_term}")

    try:
        # Initial search
        response = gmaps.places(query=search_term)
        places   = response.get("results", [])

        # Paginate through results
        while places and len(results) < max_results:
            for place in places:
                if len(results) >= max_results:
                    break

                place_id = place.get("place_id")
                if place_id in seen_ids:
                    continue
                seen_ids.add(place_id)

                try:
                    # Get detailed info for each place
                    detail = gmaps.place(
                        place_id,
                        fields=[
                            "name", "formatted_address", "formatted_phone_number",
                            "website", "rating", "user_ratings_total",
                            "type", "business_status"
                        ]
                    ).get("result", {})

                    # Skip permanently closed businesses
                    if detail.get("business_status") == "CLOSED_PERMANENTLY":
                        continue

                    name     = detail.get("name", "N/A")
                    address  = detail.get("formatted_address", "N/A")
                    phone    = detail.get("formatted_phone_number", "N/A")
                    website  = detail.get("website", "N/A")
                    rating   = str(detail.get("rating", "N/A"))
                    reviews  = str(detail.get("user_ratings_total", "N/A"))
                    types = detail.get("types", [])
                    category = types[0].replace("_", " ").title() if types else "N/A"

                    business = {
                        "name":       name,
                        "category":   category,
                        "address":    address,
                        "phone":      phone,
                        "website":    website,
                        "rating":     rating,
                        "reviews":    reviews,
                        "location":   location,
                        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }

                    results.append(business)
                    print(f"  [{len(results)}] {name} | {rating} stars | {address[:50]}")

                    # Polite delay between detail requests
                    time.sleep(random.uniform(0.3, 0.8))

                except Exception as e:
                    print(f"  [!] Error fetching details: {e}")
                    continue

            # Get next page if available
            next_page_token = response.get("next_page_token")
            if not next_page_token or len(results) >= max_results:
                break

            # Google requires a short wait before using next_page_token
            time.sleep(2)
            response = gmaps.places(
                query=search_term,
                page_token=next_page_token
            )
            places = response.get("results", [])

    except Exception as e:
        print(f"[!] Google Maps API error: {e}")

    print(f"[+] Found {len(results)} businesses")
    return results


def save_to_csv(data: list, query: str, location: str) -> str:
    """Save scraped results to a timestamped CSV file."""
    if not data:
        print("[!] No data to save.")
        return ""

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = os.path.join(
        OUTPUT_DIR,
        f"{query.replace(' ', '_')}_{location.replace(', ', '_')}_{timestamp}.csv"
    )

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"\n[✓] Saved {len(data)} businesses to: {filename}")
    return filename


if __name__ == "__main__":
    # Test run
    init_db()
    data = scrape_google_maps("restaurants", "Dhaka, Bangladesh", 10)
    save_to_csv(data, "restaurants", "Dhaka, Bangladesh")

    inserted = 0
    skipped  = 0
    for business in data:
        if insert_lead(business):
            inserted += 1
        else:
            skipped += 1
    print(f"[✓] DB: {inserted} inserted, {skipped} skipped")