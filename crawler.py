import pandas as pd
from utilities import natural_wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from detect_cards import detect_cards
def crawl(driver, wait, action):
    records = []
    cards = detect_cards(driver, wait)
    driver.execute_script("arguments[0].scrollIntoView(true)",cards[-1])

    last_page_el = driver.find_element(By.XPATH, "//li[contains(@class, 'comet-pagination-item')][last()]")
    
    last_page_text = int(last_page_el.text.strip())

    for page in range(2, last_page_text + 1, 1):

        print("|"*50)

        print("Scrapping page: ", page - 1)

        try:

            cards = detect_cards(driver, wait)
            for index, card in enumerate(cards,start = 1):
                try:
                    print("-" *50 )
                    print(f"Hovering on card {index}")
                    driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    action.move_to_element(card).perform()
                    natural_wait(1, 3)
                
                    try:
                        
                        print(f"Clicking on card {index}'s preview")
                        preview_button = card.find_element(By.CSS_SELECTOR,"span[title='See preview']")
                        wait.until(EC.element_to_be_clickable(preview_button))
                        preview_button.click()
                        print(f"Card: {index}'s preview opened")
                        natural_wait(2, 3)
                    
                    except Exception as e:
                        print(f"Error while finding {index} card's preview button ,", e)

                    try:
                        print(" Scrapping details...")
                        price = driver.find_element(By.CSS_SELECTOR,".price--current--I3Zeidd").text.strip()
                        title = driver.find_element(By.CSS_SELECTOR,".title--wrap--UUHae_g").text.strip()
                        link = card.get_attribute("href")
                        records.append({"title": title,
                                        "price": price,
                                        "url": link })
                        natural_wait(1, 3)
                    except Exception as e:
                        print("Error occured while extracting price ,", e)



                    try:
                        print("Closing preview")
                        close_button = card.find_element(By.XPATH, "//button[@type = 'button' and @aria-label = 'Close']")
                        wait.until(EC.element_to_be_clickable(close_button)).click()
                        print(f"Card {index}'s preview closed\n")
                        
                        natural_wait(3, 4)
                    except Exception as e:
                        print(f"{index} card's gave an error ,", e)
                except Exception as e:
                    print("An exception occured while interacting with card: ", e)
        
            nxt_button = wait.until(EC.element_to_be_clickable((By.XPATH,f"//li[contains(@class, 'comet-pagination-item comet-pagination-item-{page}')]")))
            driver.execute_script("arguments[0].click();", nxt_button)
            natural_wait(4, 5)
        except Exception as e:
            print("Error while searching for cards: ", e)
        
    
    return records