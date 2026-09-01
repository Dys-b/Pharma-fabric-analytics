import json
import time
from pathlib import Path

import requests


# CONFIG


URL = "https://data.medicaid.gov/api/1/datastore/sql"

RESOURCE_ID = "a613f4ae-0615-572c-812a-a381379914cd"

PAGE_SIZE = 500
PAGES_PER_FILE = 20          # 500 x 20 = 10,000 rows/file
MAX_RETRIES = 5

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "bronze"
    / "medicaid"
    / "2025"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CHECKPOINT = OUTPUT_DIR / "checkpoint.json"



# API REQUEST


def get_page(session, offset):

    query = (
        f"[SELECT * FROM {RESOURCE_ID}]"
        f"[LIMIT {PAGE_SIZE} OFFSET {offset}]"
    )

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = session.get(
                URL,
                params={"query": query},
                timeout=60
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:

            wait_time = 2 ** attempt

            print(
                f"Request failed at offset {offset}. "
                f"Attempt {attempt}/{MAX_RETRIES}: {error}"
            )

            if attempt == MAX_RETRIES:
                raise

            print(
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)



# CHECKPOINT


def save_checkpoint(
    offset,
    file_number,
    total_downloaded
):

    checkpoint = {
        "offset": offset,
        "file_number": file_number,
        "total_downloaded": total_downloaded
    }

    with open(
        CHECKPOINT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            checkpoint,
            file,
            indent=2
        )


def load_checkpoint():

    if not CHECKPOINT.exists():
        return None

    with open(
        CHECKPOINT,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)



# SAVE BATCH

def save_batch(records, file_number):

    output = (
        OUTPUT_DIR
        / f"medicaid_2025_{file_number:05d}.json"
    )

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            ensure_ascii=False
        )

    return output



# MAIN


def main():

    checkpoint = load_checkpoint()

    if checkpoint:

        offset = checkpoint["offset"]
        file_number = checkpoint["file_number"]
        total_downloaded = checkpoint["total_downloaded"]

        print(
            f"Resuming ingestion at offset {offset:,}"
        )

        print(
            f"Already downloaded: "
            f"{total_downloaded:,} records"
        )

    else:

        offset = 0
        file_number = 1
        total_downloaded = 0

        print("Starting new Medicaid ingestion")


    buffer = []

    with requests.Session() as session:

        while True:

            print(
                f"Downloading offset "
                f"{offset:,}..."
            )

            records = get_page(
                session,
                offset
            )

            record_count = len(records)

            if record_count == 0:
                print("No more records.")
                break


            buffer.extend(records)

            offset += record_count
            total_downloaded += record_count


            print(
                f"Received: {record_count:,}"
            )

            print(
                f"Total downloaded: "
                f"{total_downloaded:,}"
            )


            
            # SAVE EVERY 10,000 ROWS
        

            if len(buffer) >= (
                PAGE_SIZE
                * PAGES_PER_FILE
            ):

                output = save_batch(
                    buffer,
                    file_number
                )

                print(
                    f"Saved {len(buffer):,} rows "
                    f"to {output.name}"
                )

                buffer = []

                file_number += 1


                save_checkpoint(
                    offset,
                    file_number,
                    total_downloaded
                )


            
            # FINAL PARTIAL PAGE
        

            if record_count < PAGE_SIZE:

                print(
                    "Last API page detected."
                )

                break


            time.sleep(0.1)


  
    # SAVE REMAINING RECORDS
   

    if buffer:

        output = save_batch(
            buffer,
            file_number
        )

        print(
            f"Saved final {len(buffer):,} rows "
            f"to {output.name}"
        )

        file_number += 1


    save_checkpoint(
        offset,
        file_number,
        total_downloaded
    )


    print()
    print(
        "Medicaid ingestion completed successfully"
    )

    print(
        f"Total records: "
        f"{total_downloaded:,}"
    )


if __name__ == "__main__":
    main()