
"""Row validation: airport list loading, single-row checks, record building."""

import re
import math
from datetime import datetime


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    airports = set()

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            code = line.strip()

            if code and not code.startswith("#"):
                airports.add(code)

    return airports


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    fields = [field.strip() for field in fields]

    if any(field == "" for field in fields):
        return "MISSING_FIELD"

    flight_id, origin, destination, departure, arrival, price = fields

    if not re.fullmatch(r"[A-Za-z0-9]{2,8}", flight_id):
        return "INVALID_FLIGHT_ID"

    if not re.fullmatch(r"[A-Z]{3}", origin) or origin not in airports:
        return "INVALID_ORIGIN"

    if not re.fullmatch(r"[A-Z]{3}", destination) or destination not in airports:
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    try:
        dep_time = datetime.strptime(departure, "%Y-%m-%d %H:%M")
        if dep_time.strftime("%Y-%m-%d %H:%M") != departure:
            return "INVALID_DEPARTURE"
    except ValueError:
        return "INVALID_DEPARTURE"

    try:
        arr_time = datetime.strptime(arrival, "%Y-%m-%d %H:%M")
        if arr_time.strftime("%Y-%m-%d %H:%M") != arrival:
            return "INVALID_ARRIVAL"
    except ValueError:
        return "INVALID_ARRIVAL"

    if arr_time <= dep_time:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price_value = float(price)
        if not math.isfinite(price_value):
            return "INVALID_PRICE"
    except ValueError:
        return "INVALID_PRICE"

    if price_value <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    fields = [field.strip() for field in fields]

    return {
        "flight_id": fields[0],
        "origin": fields[1],
        "destination": fields[2],
        "departure_datetime": fields[3],
        "arrival_datetime": fields[4],
        "price": float(fields[5])
    }
