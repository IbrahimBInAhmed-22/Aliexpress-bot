from selenium import webdriver
import time
import random

def make_driver():
    #---------------------  HEADLESS ------------------------#

    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    # driver = webdriver.Chrome(options = chrome_options)
    driver = webdriver.Chrome()
    return driver
def natural_wait(low_range = 5, high_range = 20):
    wait_time = random.uniform(low_range, high_range)
    time.sleep(wait_time)