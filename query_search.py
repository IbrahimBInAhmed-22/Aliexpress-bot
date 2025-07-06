from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utilities import natural_wait
from selenium.webdriver.common.keys import Keys

def search_query(query, wait, driver):
        try:
            print("Searhing for search bar..")
            search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".search--keyword--15P08Ji")))
            print("search bar found...")
            natural_wait(3, 4)
            search_box.clear()
            natural_wait(2, 3)
            print("Search box cleared...")
            search_box.send_keys(query)
            natural_wait(1, 2)
            print(f" \"{query}\" entered in search bar...")
            search_box.send_keys(Keys.ENTER)
            print("Query Searched....")
            natural_wait(1, 3)
            return True
        except Exception as e:
            print("Error while Searchig the query... ", e)
            driver.quit()
            return False