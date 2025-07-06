from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utilities import natural_wait

def detect_cards(driver, wait):
        print(f"Searching for cards...")
        cards=()
        len_nxt = 0
        try:
            cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"a.kr_b.in_is.search-card-item")))

            while(len_nxt < len(cards)):
                len_nxt = len(cards)
                driver.execute_script("arguments[0].scrollIntoView(true)", cards [-1])
                natural_wait(5,6)
                cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"a.kr_b.in_is.search-card-item")))
        except Exception as e:
            print("Error while detecting cards ,", e)
        print("\n",len_nxt,  " Cards found. \n")
        return cards