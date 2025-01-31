# modules/handle_first_page.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    NoSuchElementException
)

from modules.driver_setup import human_delay

def handle_first_page(driver):
    """
    Runs once on the first page to open the Apollo extension.

    STEP 1: Try to click the #apollo_open_button in the main document.
    STEP 2: (Optional) If there's a second main-doc fallback selector, try that.
    STEP 3: If all else fails, switch into the older iframe and click there.
    """

    # 1) Try main doc by ID
    if try_click_apollo_main_doc(driver, button_id="apollo_open_button"):
        return  # If successful, we're done.

    # 2) [Optional] If you have another known selector in the main document, try it:
    # if try_click_apollo_main_doc(driver, css_selector=".some-other-apollo-button"):
    #     return

    # 3) Fallback to older iframe-based approach
    open_apollo_in_iframe(driver)


def try_click_apollo_main_doc(driver, button_id=None, css_selector=None):
    """
    Attempts to find and click an Apollo open button in the main document
    using either an ID or a CSS selector. Returns True if clicked successfully,
    False otherwise.

    - If 'button_id' is provided, it tries to find by ID.
    - Else if 'css_selector' is provided, it tries to find by CSS.
    """
    try:
        # Delay to let elements load on the page
        human_delay(3, 2)  # waits ~3-5 sec

        if button_id:
            # Wait for the element by ID
            open_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, button_id))
            )
        elif css_selector:
            # Wait for the element by CSS
            open_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
        else:
            return False

        # Scroll it into view
        driver.execute_script("arguments[0].scrollIntoView(true);", open_btn)
        human_delay(2, 2)  # small pause

        # Attempt clicks
        try:
            open_btn.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", open_btn)

        print(f"Opened Apollo extension via main doc "
              f"{f'ID #{button_id}' if button_id else f'CSS {css_selector}'}!")

        # Wait extra time for extension to appear
        human_delay(4, 3)  # ~4-7 seconds
        return True

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Could NOT click Apollo main doc button: {e}")
        return False
    except Exception as general_err:
        print(f"Unknown error clicking Apollo main doc button: {general_err}")
        return False


def open_apollo_in_iframe(driver):
    """
    Fallback approach:
    - Switches to the old 'linkedin-sidebar-iframe'
    - Clicks the extension button from inside the iframe
    """
    print("Attempting older iframe-based approach...")
    try:
        # Wait for the iframe
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="linkedin-sidebar-iframe"]'))
        )
        driver.switch_to.frame(iframe)
        print("Switched to the Apollo sidebar iframe.")

        # Wait a bit before clicking
        human_delay(3, 2)

        # Click the extension button within the iframe
        extension_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "#LinkedinOverlay > div > div > div:nth-child(6) "
                "> div.x_SrTzk.x_pnPas.zp-9-2-0-zp-fixed > div.x_Q33Is.apollo-opener-icon"
            ))
        )
        extension_btn.click()
        print("Opened the Apollo extension (via iframe fallback).")

        human_delay(3, 2)  # ~3-5 sec
    except Exception as e:
        print(f"Error opening Apollo in iframe: {e}")
    finally:
        driver.switch_to.default_content()
