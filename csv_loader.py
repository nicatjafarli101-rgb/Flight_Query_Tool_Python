
"""Reading CSV files into flight records and error messages."""

import csv
import os

from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
        records - valid flight records, in input order
        errors - one message per invalid row, in input order, formatted as
                 "<file name>:<line number>: <ERROR_CODE> | <free text>"
                 (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records = []
    errors = []
    seen_flights = set()

    for path in paths:
        with open(path, "r", encoding="utf-8", newline="") as file:
            for line_number, line in enumerate(file, start=1):

                if line_number == 1:
                    continue

                if not line.strip() or line.lstrip().startswith("#"):
                    continue

                fields = next(csv.reader([line]))

                error_code = validate_row(fields, airports)

                if error_code is None:
                    clean_fields = [field.strip() for field in fields]
                    flight_id = clean_fields[0]
                    departure = clean_fields[3]
                    duplicate_key = (flight_id, departure)

                    if duplicate_key in seen_flights:
                        error_code = "DUPLICATE_FLIGHT"
                    else:
                        seen_flights.add(duplicate_key)

                if error_code is not None:
                    filename = os.path.basename(path)
                    original_line = line.strip()
                    errors.append(
                        f"{filename}:{line_number}: {error_code} | {original_line}"
                    )
                else:
                    records.append(to_record(fields))

    return records, errors
