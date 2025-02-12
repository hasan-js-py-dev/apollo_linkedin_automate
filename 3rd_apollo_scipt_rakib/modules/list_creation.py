import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules.driver_setup import human_delay

def create_new_list(driver, list_name):
    """
    Full flow:
      1) Refresh the page
      2) Wait 10 seconds
      3) Open Apollo extension (via iframe)
      4) Click "Add to list" label if it appears
      5) Remove any existing lists
      6) Click "Create new list"
      7) Enter list name
      8) Click "Create list & add"
    """

    try:
        print(f"[List Creation] Attempting to create list: '{list_name}'")

        # 1) Refresh the browser
        print("[List Creation] Refreshing the page now...")
        driver.refresh()

        # 2) Wait 10 seconds before continuing
        print("[List Creation] Waiting 10 seconds after refresh...")
        time.sleep(10)

        # 3) Open Apollo extension (via iframe approach, similar to handle_first_page)
        if not open_apollo_iframe(driver):
            raise Exception("[List Creation] Could NOT open Apollo extension after refresh.")

        # 4) Click "Add to list" label if it appears
        add_to_list_btn = find_optional(
            driver,
            "//div[@class='x_S1bDQ']//label[@class='x_mPXlR']"
        )
        if add_to_list_btn:
            print("[List Creation] Found 'Add to list' button. Clicking to open sub-panel...")
            add_to_list_btn.click()
            human_delay(2, 1)
        else:
            print("[List Creation] 'Add to list' button not found. Possibly already open.")

        # 5) Remove any existing lists
        remove_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Remove')]")
        if remove_buttons:
            print(f"[List Creation] Found {len(remove_buttons)} 'Remove' buttons. Removing old lists...")
            for btn in remove_buttons:
                driver.execute_script("arguments[0].click();", btn)
                human_delay(1, 0.5)

        # 6) Find & click "Create new list"
        create_list_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(@class,'x_qe0Li') and contains(., 'Create new list')]"
            ))
        )
        print("[List Creation] 'Create new list' button found. Clicking now...")
        driver.execute_script("arguments[0].scrollIntoView(true);", create_list_button)
        create_list_button.click()
        human_delay(2, 1)

        # 7) Enter the list name
        list_name_input = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[@class='x_dJ2fA' and @data-input-box-main]//input[@placeholder='List name']"
            ))
        )
        print(f"[List Creation] Entering the desired list name: '{list_name}'")
        driver.execute_script("arguments[0].scrollIntoView(true);", list_name_input)
        list_name_input.clear()
        list_name_input.send_keys(list_name)
        human_delay(2, 1)

        # 8) Click "Create list & add"
        create_list_add_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[@type='submit' and contains(., 'Create list & add')]"
            ))
        )
        print("[List Creation] Clicking 'Create list & add'...")
        driver.execute_script("arguments[0].scrollIntoView(true);", create_list_add_button)
        create_list_add_button.click()
        human_delay(2, 1)

        print(f"[List Creation] ✅ List '{list_name}' created and added successfully!")
        return True

    except Exception as e:
        print(f"[List Creation] ❌ Failed to create list '{list_name}': {e}")
        return False

# -----------------------------------------------------------------
def open_apollo_iframe(driver):
    """
    Similar to handle_first_page's 'open_apollo_in_iframe' logic.
    1) Locate the Apollo iframe.
    2) Switch to it.
    3) Click the extension button.
    4) Switch back to main doc.
    Returns True if successful, False if error.
    """
    try:
        print("[List Creation] Attempting to open Apollo extension via iframe...")

        # 1) Locate the iframe
        iframe = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="linkedin-sidebar-iframe"]'))
        )
        driver.switch_to.frame(iframe)
        human_delay(3, 2)

        # 2) Click the extension button
        extension_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "#LinkedinOverlay > div > div > div:nth-child(6) "
                "> div.x_SrTzk.x_pnPas.zp-9-2-0-zp-fixed > div.x_Q33Is.apollo-opener-icon"
            ))
        )
        extension_btn.click()
        human_delay(3, 2)
        print("[List Creation] Apollo extension opened successfully via iframe.")
        return True

    except Exception as e:
        print(f"[List Creation] Error in open_apollo_iframe: {e}")
        return False

    finally:
        # Switch back to main doc so subsequent code isn't stuck in the iframe
        driver.switch_to.default_content()

def find_optional(driver, xpath):
    """Return the first element if found, else None."""
    elements = driver.find_elements(By.XPATH, xpath)
    return elements[0] if elements else None
