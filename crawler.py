from utilities import natural_wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from detect_cards import detect_cards
def crawl(driver, wait, action):
    cards = detect_cards(driver, wait)
    try:
        for index, card in enumerate(cards,start = 1):
            try:
                print(f"Hovering on card {index}")
                driver.execute_script("arguments[0].scrollIntoView(true);", card)
                action.move_to_element(card).perform()
                #natural_wait(3, 4)
            
                try:
                    
                    print(f"Clicking on card {index}'s preview")
                    preview_button = card.find_element(By.CSS_SELECTOR,"span[title='See preview']")
                    wait.until(EC.element_to_be_clickable(preview_button))
                    preview_button.click()
                    print(f"Card: {index}'s preview opened...")
                    natural_wait(2, 3)
                
                except Exception as e:
                    print(f"Error while finding {index} card's preview button ,", e)
                try:
                    print("Closing preview....")
                    close_button = card.find_element(By.XPATH, "//button[@type = 'button' and @aria-label = 'Close']")
                    wait.until(EC.element_to_be_clickable(close_button)).click()
                    print(f"Card {index}'s preview closed\n")
                    print("-" *50 )
                    natural_wait()
                except Exception as e:
                    print(f"{index} card's gave an error ,", e)
            except Exception as e:
                print("An exception occured while interacting with card: ", e)
        
    except Exception as e:
        print("Error while searching for cards: ", e)