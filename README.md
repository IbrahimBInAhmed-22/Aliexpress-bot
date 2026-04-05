# AliExpress Product Scraper

A modular Python web scraper built with Selenium that searches AliExpress for a given product keyword, iterates through all result pages, extracts product title, price, and URL from each card's preview panel, and saves everything to an Excel file.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [File Structure](#2-file-structure)
3. [Architecture Diagram](#3-architecture-diagram)
4. [Module Breakdown](#4-module-breakdown)
   - [main.py — Entry Point](#41-mainpy--entry-point)
   - [utilities.py — Driver & Timing](#42-utilitiespy--driver--timing)
   - [pop_up.py — Pop-up Handler](#43-pop_uppy--pop-up-handler)
   - [query_search.py — Search Input](#44-query_searchpy--search-input)
   - [detect_cards.py — Card Loader](#45-detect_cardspy--card-loader)
   - [crawler.py — Page Crawler](#46-crawlerpy--page-crawler)
   - [save_data.py — Excel Export](#47-save_datapy--excel-export)
5. [Output Format (Aliexpress.xlsx)](#5-output-format-aliexpressxlsx)
6. [Anti-Detection Strategy](#6-anti-detection-strategy)
7. [CSS Selectors Reference](#7-css-selectors-reference)
8. [Data Flow — End to End](#8-data-flow--end-to-end)
9. [Setup & Installation](#9-setup--installation)
10. [How to Run](#10-how-to-run)
11. [Known Limitations & Improvements](#11-known-limitations--improvements)
12. [Key Concepts Demonstrated](#12-key-concepts-demonstrated)



## 1. Project Overview

This scraper automates a full AliExpress search session:

1. Opens a real Chrome browser via Selenium WebDriver
2. Navigates to `aliexpress.com` and dismisses any sign-up pop-ups
3. Types a search query into the search bar and submits it
4. Detects the total number of result pages from the pagination widget
5. For each page, scrolls through every product card, hovers to reveal the preview panel, and extracts title, price, and product URL
6. Saves all records to `Aliexpress.xlsx`

The scraper uses **randomised human-like delays** between actions to reduce the risk of bot detection. All logic is split across small, single-responsibility Python modules.



## 2. File Structure

```
project/
│
├── main.py              # Entry point — orchestrates the full session
├── utilities.py         # WebDriver factory + random wait helper
├── pop_up.py            # Dismisses the AliExpress sign-up pop-up
├── query_search.py      # Types and submits the search query
├── detect_cards.py      # Finds and lazy-loads all product cards on a page
├── crawler.py           # Iterates pages, opens previews, extracts data
├── save_data.py         # Writes collected records to Aliexpress.xlsx
│
├── web.html             # Saved HTML snippet of pagination widget (reference)
└── Aliexpress.xlsx      # Output file — 27 sample records (title, price, url)
```

---

## 3. Architecture Diagram

```
main.py
│
├── make_driver()            ← utilities.py   — launches Chrome
├── WebDriverWait(driver,20) ← selenium       — global explicit wait
├── ActionChains(driver)     ← selenium       — mouse hover simulation
│
├── driver.get("aliexpress.com")
│
├── close_pop_up(wait)       ← pop_up.py      — dismiss sign-up modal
│
├── search_query(query, wait, driver)
│   └── query_search.py      — find search bar, type query, press ENTER
│
└── crawl(driver, wait, action)
    └── crawler.py
        │
        ├── detect_cards(driver, wait)   ← detect_cards.py
        │   └── scroll until no new cards load (lazy-load exhaust)
        │
        ├── read last page number from pagination widget
        │
        └── for page in range(2, last_page + 1):
            │
            ├── detect_cards()           — re-detect cards for this page
            │
            ├── for each card:
            │   ├── scrollIntoView + ActionChains.move_to_element()
            │   ├── click "See preview" button
            │   ├── extract: price, title, url (href)
            │   └── click Close button on preview
            │
            └── click page-N pagination button → natural_wait()

        └── return records[]

save_data(records)           ← save_data.py
└── pd.DataFrame → Aliexpress.xlsx
```



## 4. Module Breakdown

### 4.1 `main.py` — Entry Point

```python
query = "earbuds"
```

The only place you need to change the search keyword. Sets up the three Selenium primitives and calls each module in sequence:

| Object | Type | Purpose |
|---|---|---|
| `driver` | `webdriver.Chrome` | The browser instance |
| `wait` | `WebDriverWait(driver, 20)` | Waits up to 20 s for elements |
| `action` | `ActionChains(driver)` | Simulates mouse movements |

The entire session is wrapped in a `try/except` so unexpected timeouts print a message instead of crashing silently. `driver.quit()` is always called at the end.



### 4.2 `utilities.py` — Driver & Timing

```python
def make_driver() -> webdriver.Chrome
def natural_wait(low_range=5, high_range=20)
```

**`make_driver()`** — Creates and returns a Chrome WebDriver instance. A commented-out block shows how to switch to **headless mode** for server/CI use:

```python
# chrome_options.add_argument("--headless")
```

**`natural_wait(low, high)`** — Sleeps for a random number of seconds between `low` and `high` using `random.uniform`. This mimics human reading/thinking time and is the primary anti-bot mechanism throughout the scraper. Default range is 5–20 s; individual call sites use tighter ranges (e.g., 1–3 s between clicks).



### 4.3 `pop_up.py` — Pop-up Handler

```python
def close_pop_up(wait)
```

AliExpress often shows a sign-up/login modal on first visit. This function:
1. Waits up to 20 s for an element matching `.pop-close-btn` to become clickable
2. Waits 3–5 s (human-like pause) then clicks it
3. If the pop-up never appears (or takes too long), silently continues — the `except` block prints a message but does **not** raise, so the rest of the session proceeds normally



### 4.4 `query_search.py` — Search Input

```python
def search_query(query, wait, driver) -> bool
```

Locates the AliExpress search bar by CSS selector `.search--keyword--15P08Ji`, then:

1. Waits for it to be **clickable** (not just present)
2. Clears any existing text (`search_box.clear()`)
3. Types the query character by character via `send_keys(query)`
4. Submits with `send_keys(Keys.ENTER)`
5. Returns `True` on success, `False` on any exception (which also quits the driver)

A `False` return in `main.py` triggers an early exit — no point crawling if the search failed.



### 4.5 `detect_cards.py` — Card Loader

```python
def detect_cards(driver, wait) -> list[WebElement]
```

AliExpress search results use **infinite/lazy scroll** — not all cards are in the DOM when the page first loads. This function exhausts the lazy loader:

```python
while len_nxt < len(cards):
    len_nxt = len(cards)
    driver.execute_script("arguments[0].scrollIntoView(true)", cards[-1])
    natural_wait(5, 6)
    cards = wait.until(EC.presence_of_all_elements_located(...))
```

Think of it like pulling a tablecloth — you keep pulling (`scrollIntoView` on the last card) until nothing new falls off the edge (card count stops growing). The loop exits when two consecutive counts are equal, meaning all cards are loaded.

**CSS selector used:** `a.kr_b.in_is.search-card-item`

Returns the full list of card `WebElement` objects for the caller to iterate.



### 4.6 `crawler.py` — Page Crawler

```python
def crawl(driver, wait, action) -> list[dict]
```

The main data-collection engine. Key steps:

#### Reading the total page count

```python
last_page_el = driver.find_element(By.XPATH,
    "//li[contains(@class, 'comet-pagination-item')][last()]")
last_page_text = int(last_page_el.text.strip())
```

Finds the last `<li>` in the pagination bar (as seen in `web.html`) and reads its text as an integer. The captured sample showed 60 pages total.

#### Per-card interaction loop

For each card on the current page:

| Step | Action | Selenium API |
|---|---|---|
| 1 | Scroll card into viewport | `execute_script("arguments[0].scrollIntoView(true)")` |
| 2 | Hover over card | `ActionChains.move_to_element(card).perform()` |
| 3 | Click "See preview" | `card.find_element(By.CSS_SELECTOR, "span[title='See preview']")` |
| 4 | Extract price | `driver.find_element(By.CSS_SELECTOR, ".price--current--I3Zeidd")` |
| 5 | Extract title | `driver.find_element(By.CSS_SELECTOR, ".title--wrap--UUHae_g")` |
| 6 | Extract URL | `card.get_attribute("href")` |
| 7 | Close preview | `button[@type='button' and @aria-label='Close']` |

Each try-except is **independent** — if the preview button fails on one card, the scraper logs the error and moves to the next card rather than aborting the whole page.

#### Page navigation

```python
nxt_button = wait.until(EC.element_to_be_clickable((By.XPATH,
    f"//li[contains(@class, 'comet-pagination-item comet-pagination-item-{page}')]")))
driver.execute_script("arguments[0].click();", nxt_button)
```

Uses `execute_script` click instead of `.click()` to bypass potential overlay interception errors.



### 4.7 `save_data.py` — Excel Export

```python
def save_data(records: list[dict])
```

Converts the `records` list (each dict has `title`, `price`, `url`) to a `pandas.DataFrame` and writes it to `Aliexpress.xlsx` using `openpyxl` as the engine:

```python
with pd.ExcelWriter("Aliexpress.xlsx", engine="openpyxl") as writer:
    data.to_excel(writer, index=False)
```

The `with` block ensures the file is properly flushed and closed even if an error occurs mid-write.



## 5. Output Format (`Aliexpress.xlsx`)

The output spreadsheet (`Sheet1`) has three columns:

| Column | Example Value |
|---|---|
| `title` | `XIAOMI Bluetooth 5.3 Headphones A2 Pro Wireless Earbuds...` |
| `price` | `PKR2,180` |
| `url` | `https://www.aliexpress.com/item/1005007853891361.html?...` |

The sample output captured **27 records** across the session (prices in PKR — Pakistani Rupee, consistent with the browser locale at time of capture). Prices are stored as raw strings exactly as displayed on AliExpress, including the currency symbol and commas.



## 6. Anti-Detection Strategy

AliExpress actively detects and blocks automated browsers. The scraper uses several mitigation techniques:

| Technique | Implementation | Where |
|---|---|---|
| **Real browser** | `webdriver.Chrome()` (not headless by default) | `utilities.py` |
| **Random delays** | `random.uniform(low, high)` via `natural_wait()` | Between every action |
| **Mouse simulation** | `ActionChains.move_to_element()` before clicks | `crawler.py` |
| **ScrollIntoView** | `execute_script("arguments[0].scrollIntoView(true)")` | `detect_cards.py`, `crawler.py` |
| **JS click fallback** | `execute_script("arguments[0].click()")` for pagination | `crawler.py` |
| **Explicit waits** | `WebDriverWait` + `EC.element_to_be_clickable` | All modules |

> **Note:** Headless mode (commented out in `utilities.py`) is easier to detect and block. Run in visible mode for best results.



## 7. CSS Selectors Reference

| Element | Selector / XPath | File |
|---|---|---|
| Search bar | `.search--keyword--15P08Ji` | `query_search.py` |
| Pop-up close button | `.pop-close-btn` | `pop_up.py` |
| Product card anchor | `a.kr_b.in_is.search-card-item` | `detect_cards.py` |
| "See preview" button | `span[title='See preview']` | `crawler.py` |
| Price in preview | `.price--current--I3Zeidd` | `crawler.py` |
| Title in preview | `.title--wrap--UUHae_g` | `crawler.py` |
| Close preview button | `//button[@type='button' and @aria-label='Close']` | `crawler.py` |
| Last pagination item | `//li[contains(@class,'comet-pagination-item')][last()]` | `crawler.py` |
| Page N button | `//li[contains(@class,'comet-pagination-item-{N}')]` | `crawler.py` |

 !!!! AliExpress frequently changes its CSS class names (e.g., `kr_b`, `in_is`, `I3Zeidd`). If the scraper stops finding elements, inspect the live page and update these selectors.



## 8. Data Flow — End to End

```
1. main() runs
   └─ Chrome browser opens → aliexpress.com

2. close_pop_up()
   └─ Wait for .pop-close-btn → click → wait

3. search_query("earbuds")
   └─ Find .search--keyword--15P08Ji
   └─ Clear → type "earbuds" → ENTER
   └─ Search results page loads

4. crawl() begins
   └─ detect_cards() — scroll until all cards loaded (lazy-load exhaust)
   └─ Read last page number from pagination (e.g., 60)

5. Page loop: page 1 → 60
   └─ For each card (e.g., 48 cards/page):
       ├─ Scroll into view
       ├─ Hover (ActionChains)
       ├─ Click "See preview"
       ├─ Extract: title, price, url
       └─ Close preview

   └─ Click page-N button → wait 4-5s → repeat

6. save_data(records)
   └─ pd.DataFrame(records)
   └─ → Aliexpress.xlsx  (title | price | url)
```



## 9. Setup & Installation

### Prerequisites

- Python 3.8+
- Google Chrome (latest stable)
- ChromeDriver matching your Chrome version ([chromedriver.chromium.org](https://chromedriver.chromium.org/downloads))

### Install Dependencies

```bash
pip install selenium pandas openpyxl
```

### ChromeDriver Setup

**Option A — Manual:** Download ChromeDriver and place it in your PATH or the project folder.

**Option B — Automatic (recommended):**
```bash
pip install webdriver-manager
```

Then update `utilities.py`:
```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def make_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver
```



## 10. How to Run

### Step 1 — Set your search query

Edit `main.py`:
```python
query = "earbuds"   # ← change to any product keyword
```

### Step 2 — Run the scraper

```bash
python main.py
```

### Step 3 — Watch the output

The scraper prints progress to the console:
```
Opening AliExpress...
Pop-up Button Detected...
Pop-Up closed....
Searching for search bar..
"earbuds" entered in search bar...
Query Searched....
Searching for cards...
48 Cards found.

||||||||||||||||||||||||||||||||||||||||||||||||||
Scrapping page: 1
--------------------------------------------------
Hovering on card 1
Clicking on card 1's preview
 Scrapping details...
Closing preview
...
```

### Step 4 — Check output

`Aliexpress.xlsx` is created/overwritten in the same directory:

```
title                                    | price    | url
-----------------------------------------|----------|-------------------------------
XIAOMI Bluetooth 5.3 Headphones A2 Pro  | PKR2,180 | https://aliexpress.com/item/...
Xiaomi TWS Bluetooth Earphones Wireless | PKR2,502 | https://aliexpress.com/item/...
A6S TWS Earphones Wireless Bluetooth... | PKR1,011 | https://aliexpress.com/item/...
```

### Switching to Headless Mode

In `utilities.py`, uncomment the headless block:
```python
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
```

> Headless mode is faster but more easily detected by AliExpress.


## 11. Known Limitations & Improvements

### Current Limitations

| Issue | Detail |
|---|---|
| **Fragile CSS selectors** | AliExpress class names like `kr_b`, `I3Zeidd` are obfuscated and change frequently — selectors break without notice |
| **No pagination for page 1** | The loop starts at `page 2`; page 1 cards are detected but no next-button click is needed. However, if page 1 has lazy-load cards not yet scrolled into view, some may be missed |
| **Price as string** | Prices are stored as `"PKR2,180"` (raw text) — not parsed into numeric values, making price comparison or sorting in Excel harder |
| **Single query per run** | Only one keyword per session; no batch/multi-keyword support |
| **No resume on crash** | If the scraper crashes on page 35, it restarts from page 1 — no checkpointing |
| **No deduplication** | If a card appears on multiple pages (AliExpress sometimes shows promoted items on every page), duplicates are not filtered |
| **`re` imported but unused** | `import re` in `main.py` is never used — dead import |

### Suggested Improvements

- **Selector config file** — Store all CSS selectors in a `selectors.json` so updates don't require touching Python files
- **Numeric price parsing** — Strip currency symbol and commas, store as `float` for analysis
- **Checkpoint/resume** — Save `records` to disk after each page so a crash can resume mid-run
- **Multi-keyword batch mode** — Accept a list of queries and append all results to a single Excel file with a `query` column
- **Headless + undetected-chromedriver** — Use `undetected-chromedriver` for stealthier headless scraping
- **Proxy rotation** — Route requests through rotating proxies to avoid IP-level rate limiting on large crawls
- **Rate limiting awareness** — Detect CAPTCHA pages and pause/retry rather than crashing



## 12. Key Concepts Demonstrated

| Concept | Where it appears |
|---|---|
| **Selenium WebDriver** | Browser automation throughout all modules |
| **Explicit waits** | `WebDriverWait` + `ExpectedConditions` — prevents race conditions on dynamic content |
| **ActionChains** | Mouse hover simulation to reveal hidden preview buttons |
| **JavaScript execution** | `execute_script` for scrolling and click fallback |
| **Lazy-load exhaustion** | Scroll-until-stable loop in `detect_cards.py` |
| **CSS selectors & XPath** | Mixed use: CSS for element identity, XPath for dynamic pagination |
| **Modular design** | Single-responsibility modules — each file does exactly one job |
| **Graceful error handling** | Per-card `try/except` — one bad card never kills the whole page |
| **Randomised timing** | `random.uniform` delays mimic human behaviour |
| **pandas + openpyxl** | `pd.DataFrame` → `ExcelWriter` for structured data export |
| **Context manager** | `with pd.ExcelWriter(...)` ensures file is safely flushed on exit |



*Scraper built for educational purposes. Always comply with AliExpress Terms of Service and applicable laws when scraping. Do not use for commercial data harvesting without permission.*
