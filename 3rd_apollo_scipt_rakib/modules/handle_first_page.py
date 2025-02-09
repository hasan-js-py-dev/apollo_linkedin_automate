# modules/handle_first_page.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    NoSuchElementException
)

from modules.driver_setup import human_delay
from modules.browser_refresh import refresh_browser_if_needed
from modules.not_scraped_logger import log_not_scraped

def handle_first_page(driver, current_url):
    """
    Runs once on the first page to open the Apollo extension via the iframe approach.
    Retries up to 3 times if it fails:
      1) Refresh the browser
      2) Wait 10s
      3) Attempt to re-open the extension
    If it still fails, logs the URL to output.csv immediately and skips.
    """

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"[First Page] Attempt {attempt}/{max_attempts} to open Apollo extension via iframe...")

            # (Previously we tried main doc button by ID/CSS, but now commented out for future use)
            # if try_click_apollo_main_doc(driver, button_id="apollo_open_button"):
            #     return
            # if try_click_apollo_main_doc(driver, css_selector=".some-other-apollo-button"):
            #     return

            # Only do iframe approach:
            if open_apollo_in_iframe(driver):
                print("Apollo extension opened successfully on the first page!")
                return  # Success => done
            else:
                # If open_apollo_in_iframe returned False, raise an error to trigger retry logic
                raise TimeoutException("Could not open Apollo via iframe fallback.")

        except Exception as e:
            print(f"[First Page] Error: {e}")

            if attempt < max_attempts:
                # Refresh + wait 10 seconds, then retry
                print("[First Page] Refreshing browser, then retrying...")
                refresh_browser_if_needed(driver)
                time.sleep(10)
            else:
                # Final attempt failed => log & skip
                print(f"[First Page] Failed after {max_attempts} attempts. Logging URL & skipping.")
                log_not_scraped(current_url, str(e))
                return  # Skip page

def try_click_apollo_main_doc(driver, button_id=None, css_selector=None):
    """
    [Future use] Attempts to find/click an Apollo open button in the main document.
    Returns True if successful, False otherwise.
    """
    try:
        # Let elements load
        human_delay(3, 2)

        if button_id:
            open_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, button_id))
            )
        elif css_selector:
            open_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
        else:
            return False

        # Scroll into view & click
        driver.execute_script("arguments[0].scrollIntoView(true);", open_btn)
        human_delay(2, 2)

        try:
            open_btn.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", open_btn)

        print(f"Apollo extension opened via "
              f"{'ID=' + button_id if button_id else 'CSS=' + css_selector}!")
        human_delay(4, 3)  # Wait for extension to appear
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
      - Wait for 'linkedin-sidebar-iframe'
      - Click extension button from inside the iframe
    Returns True on success, False on error.
    """
    print("[First Page] Attempting older iframe-based approach...")
    try:
        # Locate the Apollo iframe
        iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="linkedin-sidebar-iframe"]'))
        )
        driver.switch_to.frame(iframe)

        human_delay(3, 2)

        # Click the extension button within the iframe
        extension_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "#LinkedinOverlay > div > div > div:nth-child(6) "
                "> div.x_SrTzk.x_pnPas.zp-9-2-0-zp-fixed > div.x_Q33Is.apollo-opener-icon"
            ))
        )
        extension_btn.click()
        human_delay(3, 2)
        print("Opened the Apollo extension via iframe fallback.")
        return True

    except Exception as e:
        print(f"Error opening Apollo in iframe: {e}")
        return False

    finally:
        # Always return to the main document
        driver.switch_to.default_content()
