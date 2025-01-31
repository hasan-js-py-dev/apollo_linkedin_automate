# modules/handle_each_page.py

import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules.driver_setup import human_delay
from modules.apollo_list import MY_DESIRED_LIST
from modules.browser_refresh import check_and_refresh_if_needed

def handle_each_page(driver):
    """
    1) Check if empty, refresh if needed.
    2) Switch to Apollo iframe
    3) Ensure all selected
    4) Process last action
    """
    # 1) If the page has no contacts, optionally refresh
    refreshed = check_and_refresh_if_needed(driver)
    if refreshed:
        # short wait if you want the page to settle after refresh
        human_delay(2, 1)  # 2-3 seconds

    try:
        switch_to_apollo_iframe(driver)
        ensure_all_selected(driver)
        process_last_action(driver)
    except Exception as e:
        print(f"Error processing 'Last action' or 'Add to list' flow: {e}")
    finally:
        driver.switch_to.default_content()

def switch_to_apollo_iframe(driver):
    iframe = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="linkedin-sidebar-iframe"]'))
    )
    driver.switch_to.frame(iframe)

def ensure_all_selected(driver):
    try:
        header_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.x_FsSHV.list-header"))
        )
        selection_toggle = header_div.find_element(By.CLASS_NAME, "x_ZYlnk").text.strip()

        if "Select all" in selection_toggle:
            print("No contacts are selected. Clicking 'Select all' now...")
            header_div.find_element(By.CLASS_NAME, "x_ZYlnk").click()
            human_delay(1, 0.5)  # just 1-1.5s after selecting
        else:
            print(f"Contacts appear to be already selected (Toggle text: '{selection_toggle}').")
    except Exception as e:
        print(f"Error ensuring all contacts are selected: {e}")

def process_last_action(driver):
    last_action_elem = driver.find_element(By.CSS_SELECTOR, "div.x_xCUI9")
    full_text = last_action_elem.text.strip()

    match = re.search(r'Add to list “([^”]+)”', full_text)
    if match:
        dynamic_list_name = match.group(1).strip()
        print(f"Last action shows list name: '{dynamic_list_name}'")
        if dynamic_list_name == MY_DESIRED_LIST:
            print("Last action matches our desired list! Clicking to save data...")
            driver.execute_script("arguments[0].click();", last_action_elem)
            human_delay(1, 0.5)  # short wait
        else:
            print(f"List name '{dynamic_list_name}' != '{MY_DESIRED_LIST}'. Doing full flow.")
            do_full_add_to_list(driver)
    else:
        print(f"Could not parse the list name from '{full_text}'. Doing FULL flow.")
        do_full_add_to_list(driver)

def do_full_add_to_list(driver):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='x_S1bDQ']//label[@class='x_mPXlR']"))
    ).click()
    human_delay(1, 0.5)

    remove_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Remove')]")
    for remove_button in remove_buttons:
        driver.execute_script("arguments[0].click();", remove_button)
        human_delay(0.5, 0.2)

    select_lists_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='x_pr73O']/span[@class='x_cnXw0']"))
    )
    select_lists_button.click()
    human_delay(1, 0.5)

    desired_list_elem = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//div[@data-value='{MY_DESIRED_LIST}']"))
    )
    desired_list_elem.click()
    human_delay(1, 0.5)

    apply_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Apply')]]"))
    )
    apply_button.click()
    human_delay(1, 0.5)

    add_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Add')]]"))
    )
    add_button.click()
    print("Data saved successfully (FULL add-to-list flow).")

    # Final short pause so we don't immediately do something else
    human_delay(1, 0.5)
