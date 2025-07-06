
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from utilities import make_driver
from pop_up import close_pop_up
from query_search import search_query
from crawler import crawl

def main():
    query = "earbuds"
    driver = make_driver()
    wait = WebDriverWait(driver, 20)
    action = ActionChains(driver)
    print("Opening AliExpress...")
# --------------------------------------- main loop-------------------------------- #
    try:
        driver.get("https://aliexpress.com")
        close_pop_up(wait)
        if not (search_query(query, wait, driver)):
            return
        crawl(driver, wait, action)
    except Exception as e:
        print("Timeout while surfing... " ,e)   
    driver.quit()


main()

