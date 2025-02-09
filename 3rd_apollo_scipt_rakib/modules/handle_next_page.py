# modules/handle_next_page.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from modules.driver_setup import human_delay

def click_next_page(driver):
    """
    Tries to click the 'Next' button to go to the next page.
    Returns True if successful, False otherwise.
    """
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
        )
        next_button.click()
        print("Clicked the NEXT button to navigate to the next page.")
        human_delay(5, 2)
        return True
    except TimeoutException:
        print("No more pages available or 'Next' is not clickable. Exiting loop.")
        return False
