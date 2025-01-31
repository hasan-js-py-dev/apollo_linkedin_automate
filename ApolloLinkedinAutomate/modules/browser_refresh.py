# modules/browser_refresh.py

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules.handle_first_page import handle_first_page

def check_and_refresh_if_needed(driver):
    """
    Checks if Apollo shows 'There are no contacts on this page' or the empty-state container.
    If found, refresh the page and re-open Apollo so we can try again.
    Returns True if a refresh was performed, False otherwise.
    """
    try:
        # Example 1: Check text "There are no contacts on this page"
        # Example 2: Check for the container 'x_qIMbg' or 'x_TPtEs'
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'There are no contacts on this page')]")
            )
        )
        print("Detected 'There are no contacts on this page' message. Refreshing...")

        driver.refresh()
        # Wait a bit for refresh to complete
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Page refreshed successfully.")

        # Now re-open Apollo as if it’s the first page
        handle_first_page(driver)

        return True  # A refresh was done

    except (TimeoutException, NoSuchElementException):
        # If not found, do nothing
        return False
    except Exception as e:
        print(f"Error in check_and_refresh_if_needed: {e}")
        return False
