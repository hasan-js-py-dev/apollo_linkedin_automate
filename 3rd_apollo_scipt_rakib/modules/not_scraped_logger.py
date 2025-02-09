# modules/not_scraped_logger.py

import csv
import os

OUTPUT_FILE = "output.csv"


def log_not_scraped(url, reason):
    """
    Appends a row to output.csv with the URL that failed and the reason.
    """
    file_exists = os.path.isfile(OUTPUT_FILE)

    with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # If file didn't exist before, write a header
        if not file_exists:
            writer.writerow(["URL", "Reason"])
        writer.writerow([url, reason])

    print(f"Logged failed URL to {OUTPUT_FILE}: {url} (Reason: {reason})")
