from utilities import make_driver, natural_wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def close_pop_up(wait):
    try:
            close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".pop-close-btn")))
            print("Pop-up Button Detected...")
            natural_wait(3, 5)
            close_button.click()
            natural_wait(2, 3)
            print("Pop-Up closed....")
    except Exception as e:
        print("No pop-up found or it took too long...")