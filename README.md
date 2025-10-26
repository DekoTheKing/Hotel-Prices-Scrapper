# Hotel-Prices-Scrapper
Hotel Prices for each day of the month
# 🏨 Skopje Hotel Lowest Price Tracker

This tool automatically checks and collects the **lowest available hotel prices per day** in **Skopje** from [Booking.com](https://www.booking.com).  
It searches for **rooms for 2 adults**, in **EUR**, across a predefined list of hotels.

The program visits each hotel’s Booking.com page, extracts the **lowest price for each date** in the selected month, and exports all results to an **Excel file**.

---

## 📊 What It Does
- Retrieves the **daily lowest price** for every hotel.
- Works with **multiple hotels in parallel** for faster results.
- Only includes **rooms that support at least 2 adults**.
- Automatically skips unavailable dates.
- Saves data in an easy-to-read `.xlsx` file (Excel format).

---

## 📁 Output Example
| Hotel              | Date       | Lowest Price (EUR) |
|--------------------|------------|--------------------|
| DoubleTree Hilton  | 2025-11-01 | 155.00             |
| Park Hotel & Spa   | 2025-11-01 | 132.50             |
| Limak Skopje       | 2025-11-02 | 140.00             |

---

### How to Use the .exe (Windows)
1. Locate `Skopje_Hotels_Lowest_Prices.exe`.  
2. Double-click to run — a console window will open.  
3. Enter the **year** and **month number** when prompted.  
4. Wait for the process to complete; the Excel file will appear in the same folder.

**.py Version (Python)**
1. Ensure you have Python installed.  
2. Install dependencies:
   ```bash
   pip install selenium pandas tqdm openpyxl
3. Make sure Google Chrome and ChromeDriver are installed and compatible.
   Run the script from the terminal:
   python Skopje_Hotels_Lowest_Prices.py
4. Enter the **year** and **month number** when prompted.  
5. Wait for the process to complete; the Excel file will appear in the same folder.

## ⚙️ Summary
This program simplifies hotel price tracking by automating daily searches and exporting clear, structured data — ideal for comparing hotel rates across a month in **Skopje**.

## 👤 Author
**Dejan Serafimovski – 2025**