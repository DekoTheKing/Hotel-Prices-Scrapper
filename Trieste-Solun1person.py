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
    "Hotel Solun Trieste": "https://www.booking.com/hotel/it/salonicco-srl.en-gb.html",
    
}

# === User input for start and end date (dd-mm-yyyy) ===
while True:
    try:
        start_input = input("Enter start date (dd-mm-yyyy): ")
        start_date = datetime.strptime(start_input, "%d-%m-%Y")

        if start_date.year < 2020 or start_date.year > 2050:
            print("⚠️ Please enter a year between 2020 and 2050.")
            continue
        break
    except ValueError:
        print("⚠️ Invalid format. Please use dd-mm-yyyy.")

while True:
    try:
        end_input = input("Enter end date (dd-mm-yyyy): ")
        end_date = datetime.strptime(end_input, "%d-%m-%Y")

        if end_date < start_date:
            print("⚠️ End date must be after or equal to start date.")
            continue

        if (end_date - start_date).days > 60:
            print("⚠️ Please select a maximum range of 60 days.")
            continue

        break
    except ValueError:
        print("⚠️ Invalid format. Please use dd-mm-yyyy.")


# === Worker function for each hotel ===
def fetch_hotel_prices(hotel_name, url):
    driver = webdriver.Chrome()
    driver.maximize_window()

    data = []
    current_date = start_date

    try:
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)

            full_url = (
                f"{url}?checkin={current_date.strftime('%Y-%m-%d')}"
                f"&checkout={next_date.strftime('%Y-%m-%d')}"
                f"&group_adults=1&no_rooms=1&selected_currency=EUR"
            )

            driver.get(full_url)
            time.sleep(2)

            # Accept cookies
            try:
                cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
                cookie_button.click()
                time.sleep(1)
            except:
                pass

            # Wait for table
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

            # Extract prices (only rooms for 1 adult)
            prices = []
            rows = driver.find_elements(By.CSS_SELECTOR, "#hprt-table tbody tr.js-rt-block-row")

            for row in rows:
                try:
                    adult_icons = row.find_elements(
                        By.CSS_SELECTOR,
                        "td.hprt-table-cell-occupancy span.c-occupancy-icons__adults i"
                    )

                    if len(adult_icons) != 1:
                        continue

                    price_span = row.find_element(
                        By.CSS_SELECTOR,
                        "td.hprt-table-cell-price span"
                    )

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

filename = f"Skopje_Hotel_Prices_{start_date.strftime('%d-%m-%Y')}_to_{end_date.strftime('%d-%m-%Y')}.xlsx"

df.to_excel(filename, index=False)

print(f"\n✅ Data exported successfully: {filename}")