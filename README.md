# AliExpress Intelligent Market Scraper

A modular, robust Python automation tool designed to scrape product data from AliExpress while bypassing modern anti-bot detections.

## 🚀 Key Features
- **Human-Mimicry:** Uses randomized wait times and ActionChains (hovering/scrolling) to simulate real human browsing.
- **Dynamic Content Handling:** Specifically designed to handle "Lazy Loading" and AJAX-rendered product cards.
- **Automated Interaction:** Not just a text-scraper; it automatically closes pop-ups and interacts with "See Preview" buttons to extract deeper product details.
- **Auto-Pagination:** Detects the total number of pages and navigates through the entire search result set automatically.
- **Data Export:** Seamlessly exports all scraped data (Title, Price, Link) into a structured Excel (.xlsx) file using Pandas.

## 🛠 Tech Stack
- **Language:** Python 3.x
- **Automation:** Selenium WebDriver
- **Data Analysis:** Pandas, OpenPyXL
- **Design Pattern:** Modular Architecture (Separation of concerns for crawling, searching, and saving).

## 📂 Module Descriptions
- `main.py`: The entry point that orchestrates the driver, search, and crawl process.
- `crawler.py`: The core engine that handles page navigation and data extraction.
- `detect_cards.py`: Manages the "Infinite Scroll" logic to ensure all products are loaded in the DOM.
- `pop_up.py`: A specialized handler to detect and close promotional modals that block the UI.
- `utilities.py`: Contains helper functions for driver configuration (including Headless mode) and naturalized delays.

## ⚙️ How It Works
1. **Initialization:** Launches a Chrome instance (Headless option available).
2. **Bypass Pop-ups:** Immediately scans for and closes any "Welcome" modals.
3. **Search:** Enters the user's query and triggers the search.
4. **Scroll & Detect:** Scrolls through the page to trigger lazy-loading of product images and details.
5. **Extract:** Hovers over each product, opens the preview, and records the data.
6. **Paginate:** Clicks the next page until the entire result set is captured.
7. **Save:** Compiles a DataFrame and writes to `Aliexpress.xlsx`.

## 🔧 Installation & Setup
1. Install requirements: `pip install selenium pandas openpyxl`
2. Ensure you have the Chrome browser installed.
3. Run `python main.py`.

## ⚖️ Disclaimer
This tool is for educational purposes only. Always respect the `robots.txt` of a website and use scraping tools responsibly.
