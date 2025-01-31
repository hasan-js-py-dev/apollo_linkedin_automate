# modules/driver_setup.py

import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def human_delay(base=20, var=10):
    """
    Adds a realistic random delay: base ± random(0, var).
    e.g. human_delay(3,2) -> sleeps between 3 and 5 seconds
    """
    time.sleep(base + random.uniform(0, var))

def get_driver(user_data_dir, profile_dir):
    """
    Configure and return a Selenium Chrome WebDriver.
    Suppresses navigator.webdriver and other automation flags.
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(fr"--user-data-dir={user_data_dir}")
    chrome_options.add_argument(f"--profile-directory={profile_dir}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Suppress navigator.webdriver
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """
        },
    )

    return driver

def simulate_slow_scrolling(driver, steps=3):
    """
    Slowly scroll down the page in small increments, waiting
    randomly between each scroll for 3–5 seconds, to appear more human.
    """
    for _ in range(steps):
        # Scroll a fraction of the screen height
        driver.execute_script(
            "window.scrollBy(0, document.documentElement.clientHeight / 4);"
        )
        # Wait 3–5 sec
        human_delay(3, 2)
    print("Finished slow scrolling.")

# Optionally remove or keep do_random_click if you want no random clicks at all:
"""
def do_random_click(driver):
    # This function is no longer called in main.py.
    try:
        x_offset = random.randint(100, 300)
        y_offset = random.randint(100, 500)
        driver.execute_script(
            f"document.elementFromPoint({x_offset}, {y_offset}).click();"
        )
        print(f"Random click at ({x_offset}, {y_offset}) done.")
        human_delay(2, 2)
    except Exception as e:
        print(f"Random click failed: {e}")
"""
