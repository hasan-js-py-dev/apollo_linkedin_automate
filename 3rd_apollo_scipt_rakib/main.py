# main.py

import random
import time
from modules.driver_setup import get_driver
from modules.prompt_url import get_base_url
from modules.handle_first_page import handle_first_page
from modules.handle_each_page import handle_each_page
from modules.handle_next_page import click_next_page

# Possible random navigation delays (seconds)
NAVIGATION_DELAYS = [16, 20, 24, 28, 32]

def main():
    try:
        driver = get_driver(
            user_data_dir=r"D:\3rd_Chrome_rakib_linkedin_apollo",  # Adjust if needed
            profile_dir="Profile 19"
        )

        # 1) Get the start page, load it
        base_url = get_base_url()
        driver.get(base_url)
        print("Page loaded successfully!")

        # 2) Open Apollo on the first page
        #    (handle_first_page will retry 3 times & log if it fails all 3)
        current_page_url = driver.current_url
        handle_first_page(driver, current_page_url)

        # 3) Keep track of last random delay so we don't repeat
        last_delay = None

        # 4) Loop over pages
        while True:
            current_page_url = driver.current_url

            # Process the current page
            # handle_each_page will also retry 3 times & log if it fails
            handle_each_page(driver, current_page_url)

            # Choose a new random delay that isn't the same as the last one
            chosen_delay = pick_non_repeating_delay(NAVIGATION_DELAYS, last_delay)
            last_delay = chosen_delay

            print(f"Current page: {current_page_url}")
            print(f"Spending {chosen_delay} seconds on this page...")
            time.sleep(chosen_delay)

            print("Moving to the next page...")
            has_next = click_next_page(driver)
            if not has_next:
                break

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Browser remains open. Close it manually if needed.")

    while True:
        pass


def pick_non_repeating_delay(delay_options, last_delay):
    """
    Picks a random delay from `delay_options` that is NOT the same as `last_delay`.
    If by chance the random pick equals `last_delay`, it retries until it gets a different value.
    """
    if len(delay_options) == 1:
        return delay_options[0]

    new_delay = random.choice(delay_options)
    while new_delay == last_delay:
        new_delay = random.choice(delay_options)
    return new_delay


if __name__ == "__main__":
    main()
