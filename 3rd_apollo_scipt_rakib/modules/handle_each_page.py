# modules/handle_each_page.py

import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules.driver_setup import human_delay
from modules.apollo_list import MY_DESIRED_LIST
from modules.browser_refresh import check_and_refresh_if_needed, refresh_browser_if_needed
from modules.handle_first_page import open_apollo_in_iframe
from modules.not_scraped_logger import log_not_scraped

def handle_each_page(driver, current_url):
    """
    1) check_and_refresh_if_needed -> if 'no contacts' found, refresh once
    2) Try up to 3 times to:
       - Switch to Apollo iframe
       - Ensure all selected
       - Process last action (or do_full_add_to_list)
      If an error occurs:
       - Refresh + wait 10s
       - Re-open Apollo extension (since extension closes after refresh)
       - Retry
    3) If still failing after 3 attempts, log to CSV & skip page.
    """

    # 1) Optional refresh if 'no contacts'
    refreshed = check_and_refresh_if_needed(driver)
    if refreshed:
        human_delay(2, 1)

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            print(f"[Each Page] Attempt {attempt}/{max_attempts}...")

            # Switch to iframe
            switch_to_apollo_iframe(driver)

            # Ensure all selected
            ensure_all_selected(driver)

            # Add to list or do full flow
            process_last_action(driver)

            # Success => break out
            break

        except Exception as e:
            print(f"[Each Page] Error on attempt {attempt}: {e}")

            if attempt < max_attempts:
                print("[Each Page] Refreshing browser & re-opening Apollo, then retrying...")
                refresh_browser_if_needed(driver)
                time.sleep(10)  # must wait 10s after refresh
                open_apollo_in_iframe(driver)  # re-open extension
                human_delay(2, 1)  # short wait for extension to load
            else:
                print(f"[Each Page] Failed after {max_attempts} attempts. Logging & skipping this page.")
                log_not_scraped(current_url, str(e))
                return

    # Switch back to main doc each time
    driver.switch_to.default_content()


def switch_to_apollo_iframe(driver):
    """
    Switch to the existing Apollo sidebar iframe.
    Raises an exception if not found in 20s.
    """
    iframe = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="linkedin-sidebar-iframe"]'))
    )
    driver.switch_to.frame(iframe)


def ensure_all_selected(driver):
    """
    If 'Select all' is available, click it. Otherwise, do nothing.
    """
    try:
        header_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.x_FsSHV.list-header"))
        )
        selection_toggle = header_div.find_element(By.CLASS_NAME, "x_ZYlnk").text.strip()

        if "Select all" in selection_toggle:
            print("[Each Page] No contacts selected. Clicking 'Select all'...")
            header_div.find_element(By.CLASS_NAME, "x_ZYlnk").click()
            human_delay(1, 0.5)
        else:
            print(f"[Each Page] Contacts already selected (Toggle text: '{selection_toggle}').")
    except Exception as e:
        print(f"Error ensuring all contacts are selected: {e}")


def process_last_action(driver):
    """
    Check if last action = "Add to list “MY_DESIRED_LIST”".
      - If yes, just click to save.
      - Otherwise, do do_full_add_to_list.
    """
    last_action_elem = driver.find_element(By.CSS_SELECTOR, "div.x_xCUI9")
    full_text = last_action_elem.text.strip()

    match = re.search(r'Add to list “([^”]+)”', full_text)
    if match:
        dynamic_list_name = match.group(1).strip()
        print(f"[Each Page] Last action shows list: '{dynamic_list_name}'")

        if dynamic_list_name == MY_DESIRED_LIST:
            print("[Each Page] Matches desired list! Clicking to save data...")
            driver.execute_script("arguments[0].click();", last_action_elem)
            human_delay(1, 0.5)
        else:
            print(f"[Each Page] Different list '{dynamic_list_name}'. Doing full flow.")
            do_full_add_to_list(driver)
    else:
        print(f"[Each Page] Could not parse the list name from '{full_text}'. Doing FULL flow.")
        do_full_add_to_list(driver)


def do_full_add_to_list(driver):
    """
    The 'full flow' to manually add contacts to the desired list.
    Retries up to 3 times if something fails.
    """
    attempts = 3
    for attempt in range(1, attempts + 1):
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class='x_S1bDQ']//label[@class='x_mPXlR']"))
            ).click()
            human_delay(1, 0.5)

            remove_buttons = driver.find_elements(
                By.XPATH, "//button[contains(@aria-label, 'Remove')]"
            )
            for remove_button in remove_buttons:
                driver.execute_script("arguments[0].click();", remove_button)
                human_delay(0.5, 0.2)

            select_lists_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class='x_pr73O']/span[@class='x_cnXw0']"))
            )
            select_lists_button.click()
            human_delay(1, 0.5)

            desired_list_elem = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@data-value='{MY_DESIRED_LIST}']"))
            )
            desired_list_elem.click()
            human_delay(1, 0.5)

            apply_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[span[contains(text(), 'Apply')]]"))
            )
            apply_button.click()
            human_delay(1, 0.5)

            add_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[span[contains(text(), 'Add')]]"))
            )
            add_button.click()
            print("[Each Page] Data saved successfully (FULL flow).")

            human_delay(1, 0.5)
            return

        except Exception as e:
            print(f"[Each Page] Error in do_full_add_to_list attempt {attempt}/{attempts}: {e}")
            if attempt < attempts:
                print("[Each Page] Retrying do_full_add_to_list flow...")
                human_delay(2, 1)
            else:
                # Re-raise so handle_each_page can log/skip
                raise e
