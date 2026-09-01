import json
import time
from pathlib import Path

import requests

#CONFIGURATION

URL = "https://api.fda.gov/drug/ndc.json"

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "bronze"
    / "ndc"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LIMIT = 100
MAX_RETRIES = 3

# HTTP REQUESTS

def get_page(url):
    for attempt in range(1, MAX_RETRIES + 1):

        try:
            response = requests.get(
                url,
                timeout=30
            )

            response.raise_for_status()

            return response

        except requests.RequestException as error:

            print(
                f"Attempt {attempt} failed: {error}"
            )

            if attempt == MAX_RETRIES:
                raise

            time.sleep(5)

# RAW DATA PERSISTENCE

def save_page(data, page_number):

    output = OUTPUT_DIR / f"ndc_{page_number:05d}.json"

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )

    return output

# PAGINATION

def get_next_url(response):

    link = response.links.get("next")

    if link:
        return link["url"]

    return None
# CHECKPOINT
CHECKPOINT = OUTPUT_DIR / "checkpoint.json"

#SAVE CHECKPOINT

def save_checkpoint(next_url, next_page, total_downloaded):
    checkpoint = {
        "next_url": next_url,
        "next_page": next_page,
        "total_downloaded": total_downloaded
    }

    with open(CHECKPOINT, "w", encoding="utf-8") as file:
        json.dump(checkpoint, file, indent=2)

# LOAD CHECKPOINT

def load_checkpoint():
    if not CHECKPOINT.exists():
        return None

    with open(CHECKPOINT, "r", encoding="utf-8") as file:
        return json.load(file)

#INGESTION PIPELINE

def main():

    checkpoint = load_checkpoint()

    if checkpoint:
        current_url = checkpoint["next_url"]
        page_number = checkpoint["next_page"]
        total_downloaded = checkpoint["total_downloaded"]

        print(
            f"Resuming from page {page_number} "
            f"({total_downloaded:,} records already downloaded)"
        )

    else:
        current_url = f"{URL}?limit={LIMIT}"
        page_number = 1
        total_downloaded = 0

        print("Starting new ingestion")

    while current_url:

        print(f"Downloading page {page_number}...")

        response = get_page(current_url)
        data = response.json()

        results = data.get("results", [])

        output = save_page(
            data,
            page_number
        )

        total_downloaded += len(results)

        next_url = get_next_url(response)

        save_checkpoint(
            next_url,
            page_number + 1,
            total_downloaded
        )

        print(
            f"Page {page_number}: "
            f"{len(results)} records"
        )

        print(
            f"Total downloaded: "
            f"{total_downloaded:,}"
        )

        print(f"Saved: {output.name}")

        current_url = next_url
        page_number += 1

        time.sleep(0.2)

    print()
    print("Ingestion completed successfully")
    print(f"Total records: {total_downloaded:,}")


if __name__ == "__main__":
    main()