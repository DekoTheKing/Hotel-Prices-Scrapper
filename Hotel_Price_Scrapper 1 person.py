from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

# === Hotels setup ===
hotels = {
    "DoubleTree by Hilton": "https://www.booking.com/hotel/mk/doubletree-by-hilton-skopje.en-gb.html",
    #"Park Hotel & Spa": "https://www.booking.com/hotel/mk/park-skopje.en-gb.html",
    #"Holiday Inn": "https://www.booking.com/hotel/mk/holiday-inn-skopje.en-gb.html",
    "Limak": "https://www.booking.com/hotel/mk/limak-skopje-luxury.en-gb.html",
    "Panoramika": "https://www.booking.com/hotel/mk/design-panoramika.en-gb.html",
    #"Alexandar Palace": "https://www.booking.com/hotel/mk/aleksandar-palace-hotel-amp-spa.en-gb.html",
    #"Alexandar II": "https://www.booking.com/hotel/mk/alexandar-ii.en-gb.html",
    #"Best Western": "https://www.booking.com/hotel/mk/best-western-turist.en-gb.html",
    #"Alexandar Square": "https://www.booking.com/hotel/mk/alexandar-square-boutique.en-gb.html",
    #"Stone Bridge": "https://www.booking.com/hotel/mk/stone-bridge.en-gb.html",
    #"Bliss": "https://www.booking.com/hotel/mk/bliss-palace-amp-spa.en-gb.html"
}

# === User input for year and month with validation ===
while True:
    try:
        year = int(input("Enter year (e.g., 2025): "))
        if year < 2020 or year > 2100:
            print("⚠️  Please enter a year between 2020 and 2100.")
            continue
        break
    except ValueError:
        print("⚠️  Invalid input. Please enter a valid year.")

while True:
    try:
        month = int(input("Enter month number (1–12): "))
        if month < 1 or month > 12:
            print("⚠️  Please enter a month between 1 and 12.")
            continue
        break
    except ValueError:
        print("⚠️  Invalid input. Please enter a valid month number.")

start_date = datetime(year, month, 1)
end_date = (start_date + timedelta(days=32)).replace(day=1)


# === Worker function for each hotel ===
def fetch_hotel_prices(hotel_name, url):
    driver = webdriver.Chrome()
    driver.maximize_window()

    data = []
    current_date = start_date

    try:
        while current_date < end_date:
            next_date = current_date + timedelta(days=1)
            full_url = (
                f"{url}?checkin={current_date.strftime('%Y-%m-%d')}"
                f"&checkout={next_date.strftime('%Y-%m-%d')}"
                f"&group_adults=1&no_rooms=1&selected_currency=EUR"
            )

            driver.get(full_url)
            time.sleep(2)

            # Accept cookies if present
            try:
                cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
                cookie_button.click()
                time.sleep(1)
            except:
                pass

            # Wait for price table
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#hprt-table tbody tr.js-rt-block-row")
                    )
                )
            except:
                data.append({
                    "Hotel": hotel_name,
                    "Date": current_date.strftime("%Y-%m-%d"),
                    "Lowest Price (EUR)": "Not available"
                })
                current_date += timedelta(days=1)
                continue

            # Extract prices for rooms that can host at least 2 adults
            prices = []
            rows = driver.find_elements(By.CSS_SELECTOR, "#hprt-table tbody tr.js-rt-block-row")
            for row in rows:
                try:
                    adult_icons = row.find_elements(
                        By.CSS_SELECTOR, "td.hprt-table-cell-occupancy span.c-occupancy-icons__adults i"
                    )
                    if len(adult_icons) != 1:
                        continue

                    price_span = row.find_element(By.CSS_SELECTOR, "td.hprt-table-cell-price span")
                    price_text = price_span.text.replace("€", "").replace(",", "").strip()
                    if price_text:
                        prices.append(float(price_text))
                except:
                    continue

            lowest_price = min(prices) if prices else "Not available"

            data.append({
                "Hotel": hotel_name,
                "Date": current_date.strftime("%Y-%m-%d"),
                "Lowest Price (EUR)": lowest_price
            })

            current_date += timedelta(days=1)

    finally:
        driver.quit()

    return data


# === Run hotels in parallel (3 instances) ===
all_data = []
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(fetch_hotel_prices, name, url) for name, url in hotels.items()]
    for f in tqdm(as_completed(futures), total=len(futures), desc="Fetching hotel data"):
        all_data.extend(f.result())

# === Export to Excel ===
df = pd.DataFrame(all_data)
month_name = start_date.strftime("%B")
filename = f"Skopje_Hotel_Lowest_Prices_{month_name}_{year}.xlsx"
df.to_excel(filename, index=False)

print(f"\n✅ Data exported successfully: {filename}")
